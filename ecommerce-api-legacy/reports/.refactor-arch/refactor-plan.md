# Plano de Refatoração MVC - ecommerce-api-legacy

## Entradas

- Relatório de auditoria: `reports/audit-ecommerce-api-legacy.md`
- Arquivo de estado: `reports/.refactor-arch/STATE.md`
- Aprovado em: 2026-07-11 20:48:53 -0300, resposta afirmativa `s` do usuário

## Arquitetura Alvo

A aplicação continuará em JavaScript CommonJS, Express e SQLite, sem dependências novas. `server.js` será a raiz de composição executável; `app.js` criará o Express; configuração virá do ambiente; `db/` cuidará da conexão/schema; repositories encapsularão SQL; services executarão checkout, relatório e exclusão; controllers adaptarão resultados para HTTP; routes declararão endpoints; middlewares cuidarão de autenticação e erros. O contrato de caminhos e campos essenciais será preservado.

## Estrutura alvo

```text
src/
|-- app.js
|-- server.js
|-- config/index.js
|-- db/{connection,initialize,sqlite}.js
|-- errors/AppError.js
|-- repositories/{user,course,enrollment,payment,audit,report}Repository.js
|-- services/{password,checkout,financialReport,user}Service.js
|-- validators/checkoutValidator.js
|-- controllers/{checkout,financialReport,user}Controller.js
|-- routes/{checkout,admin,user}Routes.js
`-- middlewares/{adminAuth,errorHandler}.js
```

## Mapeamento de Camadas

| Responsabilidade atual | Arquivos atuais | Camada alvo | Arquivos alvo | Justificativa |
|---|---|---|---|---|
| configuração e segredos | `src/utils.js` | configuração | `src/config/index.js` | ambiente e validação central |
| conexão, schema e seeds | `src/AppManager.js` | db | `src/db/*` | ciclo de vida explícito e testável |
| SQL operacional | `src/AppManager.js` | repositories | `src/repositories/*` | isolar persistência e consultas |
| checkout e pagamento | `src/AppManager.js` | services | `src/services/checkoutService.js` | caso de uso e transação sem HTTP |
| relatório e exclusão | `src/AppManager.js` | services | services e repositories próprios | remover N+1 e garantir integridade |
| adaptação HTTP | `src/AppManager.js` | controllers | `src/controllers/*` | respostas e status fora do domínio |
| declaração de endpoints | `src/AppManager.js` | routes/views | `src/routes/*` | rotas finas e explícitas |
| autenticação e erros | ausente/espalhado | middlewares | `src/middlewares/*` | segurança e erro transversais |
| bootstrap | `src/app.js`, `AppManager` | composition root | `src/app.js`, `src/server.js` | separar criação do app de `listen` |

## Matriz de Cobertura dos Achados

| ID do achado | Severidade | Decisão | Etapas do plano | Validação | Risco residual |
|---|---|---|---|---|---|
| AP-02 | CRITICAL | FIX | P01, P08 | busca de padrões de segredo e boot com ambiente | segredos já expostos devem ser rotacionados fora do código |
| AP-03 | CRITICAL | FIX | P06 | 401 sem header, 503 sem configuração e 200 com chave válida | API key é mecanismo simples; identidade/roles podem evoluir |
| AP-07 | CRITICAL | FIX | P02, P03 | hashes com `scrypt`, salt e ausência de texto puro | não há login/migração de usuários legados neste escopo |
| AP-08 | CRITICAL | FIX | P02, P04 | busca de logs de cartão/chave e smoke de checkout | observabilidade fica mínima por segurança |
| AP-04 | HIGH | FIX | P03, P04, P05, P06, P07, P08 | dependências direcionais e remoção de `AppManager` | mais arquivos aumentam navegação, compensada por coesão |
| AP-05 | HIGH | FIX | P04, P05 | controller sem SQL/regra e teste do service | simulação de gateway ainda é local, mas isolada |
| AP-06 | HIGH | FIX | P03, P04 | transação com rollback e foreign keys/cascade | SQLite continua em memória conforme contrato atual |
| AP-09 | MEDIUM | FIX | P03, P04 | relatório usa uma consulta com JOIN | agregação ainda ocorre parcialmente em memória sobre um result set |
| AP-10 | MEDIUM | FIX | P02, P08 | ausência de cache global mutável | cache removido por não ter requisito observável |
| AP-11 | MEDIUM | FIX | P05 | testes de payload inválido e validator isolado | nomes externos abreviados são preservados por compatibilidade |
| AP-12 | MEDIUM | FIX | P01, P03, P05, P06 | middleware central e erros encaminhados via `next` | mensagens legadas principais serão preservadas quando seguras |
| AP-14 | LOW | FIX | P04, P05 | revisão estática de nomes/constantes | campos abreviados persistem apenas na borda HTTP |
| AP-15 | LOW | FIX | P08 | busca de imports/arquivos legados | nenhum |

## Decisões Arquiteturais

| ID | Decisão | Motivo | Consequência |
|---|---|---|---|
| ADR-01 | manter CommonJS, Express e sqlite3 | reduzir risco e preservar stack | sem migração para ESM/ORM |
| ADR-02 | usar `crypto.scrypt` nativo | corrigir senha sem dependência nova | hashing assíncrono encapsulado em service |
| ADR-03 | adaptar callbacks SQLite para Promises | permitir services/transações legíveis | wrappers internos passam a ser a única porta ao driver |
| ADR-04 | exigir `x-admin-api-key` nas rotas financeira e de exclusão | corrigir exposição aprovada | clientes administrativos precisam enviar chave configurada |
| ADR-05 | sem chave administrativa, responder 503 | falha segura sem segredo default | app inicia, mas operações administrativas exigem configuração |
| ADR-06 | habilitar foreign keys e cascata para usuário | eliminar órfãos aprovados no relatório | resposta de exclusão será corrigida para refletir consistência |

## Etapas de Refatoração

### P01 - Fundação de configuração e erros
- Objetivo: extrair ambiente, erro de aplicação e tratamento central.
- Achados cobertos: AP-02, AP-12.
- Arquivos esperados: `src/config/index.js`, `src/errors/AppError.js`, `src/middlewares/errorHandler.js`.
- Restrições: nenhum segredo padrão; porta 3000 preservada.
- Validação: leitura estática, imports e respostas de erro controladas.

### P02 - Segurança e remoção de estado global
- Objetivo: criar hashing scrypt e eliminar logging/cache sensível/global.
- Achados cobertos: AP-07, AP-08, AP-10.
- Arquivos esperados: `src/services/passwordService.js`.
- Restrições: não registrar cartão, senha ou chave.
- Validação: formato salt:hash e busca de padrões proibidos.

### P03 - Banco e repositories
- Objetivo: encapsular SQLite, schema, seeds, consultas, foreign keys e transações.
- Achados cobertos: AP-04, AP-06, AP-07, AP-09, AP-12.
- Arquivos esperados: `src/db/*`, `src/repositories/*`.
- Restrições: SQLite em memória e seeds funcionais preservados.
- Validação: inicialização, rollback e consulta financeira única.

### P04 - Services de domínio
- Objetivo: extrair checkout, relatório e exclusão com regras nomeadas.
- Achados cobertos: AP-04, AP-05, AP-06, AP-08, AP-09, AP-14.
- Arquivos esperados: `src/services/checkoutService.js`, `financialReportService.js`, `userService.js`.
- Restrições: manter sucesso/recusa/curso ausente e JSON essencial.
- Validação: testes de services e smoke endpoints.

### P05 - Validação e controllers
- Objetivo: centralizar validação e adaptar casos de uso para HTTP.
- Achados cobertos: AP-04, AP-05, AP-11, AP-12, AP-14.
- Arquivos esperados: validator e três controllers.
- Restrições: manter nomes externos `usr`, `eml`, `pwd`, `c_id`, `card`.
- Validação: payload inválido 400, recurso ausente 404, recusa 400.

### P06 - Rotas, autenticação e middlewares
- Objetivo: declarar rotas finas e proteger operações administrativas.
- Achados cobertos: AP-03, AP-04, AP-12.
- Arquivos esperados: `src/routes/*`, `src/middlewares/adminAuth.js`.
- Restrições: preservar métodos e caminhos.
- Validação: matriz 503/401/200 de autenticação e busca de SQL nas routes.

### P07 - Raiz de composição e inicialização
- Objetivo: construir dependências em `server.js` e app testável em `app.js`.
- Achados cobertos: AP-04.
- Arquivos esperados: `src/app.js`, `src/server.js`, `package.json`.
- Restrições: `npm start` continua sendo o comando público.
- Validação: processo inicia na porta configurada e banco faz seed.

### P08 - Limpeza e documentação operacional
- Objetivo: remover legado/resíduos e documentar ambiente/autorização.
- Achados cobertos: AP-02, AP-04, AP-10, AP-15.
- Arquivos esperados: `src/AppManager.js`, `src/utils.js`, `README.md`, `api.http`.
- Restrições: remover arquivos antigos somente após imports migrarem.
- Validação: busca por imports legados, segredos e estado morto.

### P09 - Validação final
- Objetivo: executar regressão funcional e arquitetural e registrar limitações.
- Achados cobertos: todos.
- Arquivos esperados: testes e `validation-report.md`.
- Restrições: não mascarar falhas.
- Validação: testes automatizados, inicialização, smoke HTTP e varredura arquitetural.

## Contrato dos Endpoints a Preservar

| Método | Caminho | Comportamento atual | Validação |
|---|---|---|---|
| POST | `/api/checkout` | aceita campos abreviados, retorna `{ msg, enrollment_id }` em sucesso | sucesso, recusa, curso inexistente e payload inválido |
| GET | `/api/admin/financial-report` | lista `{ course, revenue, students }` | autenticação e shape com seeds |
| DELETE | `/api/users/:id` | exclui usuário | autenticação, status 200 e integridade referencial |

Mudança aprovada de segurança: os dois endpoints administrativos passam a exigir `x-admin-api-key`. Mudança aprovada de integridade: a mensagem de exclusão deixa de afirmar que há dados órfãos.

## Controles de Risco

- Atualizar `STATE.md` antes/depois de cada tarefa e não avançar após falha não resolvida.
- Não adicionar dependência nem alterar os nomes públicos dos endpoints.
- Manter queries parametrizadas.
- Testar com porta efêmera/controlada e encerrar o processo após smoke.
- Preservar artefatos preexistentes; apenas `reports/` foi criado nesta execução antes da Fase 3.
