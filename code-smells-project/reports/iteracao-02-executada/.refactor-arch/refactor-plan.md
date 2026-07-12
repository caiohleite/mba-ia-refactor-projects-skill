# Plano de Refatoração MVC - code-smells-project

## Entradas

- Relatório de auditoria: `reports/audit-code-smells-project.md`
- Arquivo de estado: `reports/.refactor-arch/STATE.md`
- Aprovado em: 2026-07-11, pela resposta explícita `s` do usuário
- Escopo aprovado: hardening localizado dos sete achados; a estrutura MVC existente será mantida

## Arquitetura Alvo

Manter o fluxo atual `views -> controllers -> services -> repositories -> SQLite`, acrescentando uma camada `middlewares` para autenticação/autorização e retirando DDL/seed do boot padrão. Configuração continuará centralizada em `loja/config.py`; regras de ownership ficarão em services; rotas apenas aplicarão guards e adaptarão HTTP. O banco terá inicialização/migração explícita, constraints e política coerente de soft delete.

## Mapeamento de Camadas

| Responsabilidade atual | Arquivos atuais | Camada alvo | Arquivos alvo | Justificativa |
|---|---|---|---|---|
| Configuração de app | `loja/config.py` | Configuração | `loja/config.py` | adicionar flags seguras de banco, seed, CORS e cookie |
| Schema e seed no boot | `loja/database.py`, `loja/__init__.py` | Infraestrutura/CLI | mesmos arquivos, com comandos Flask explícitos | evitar efeito persistente implícito |
| Persistência de produtos/usuários/pedidos | `loja/repositories/*.py` | Repositories | mesmos arquivos | manter SQL isolado e adicionar constraints/política de deleção |
| Regras de negócio | `loja/services/*.py` | Services | mesmos arquivos | preservar regras e adicionar ownership/políticas nomeadas |
| Autenticação ausente | rotas sem guard | Middleware | `loja/middlewares/auth.py` | centralizar identidade, papel e ownership de rota |
| Coordenação HTTP | `loja/controllers/*.py`, `loja/views/*.py` | Controllers/Views | mesmos arquivos | preservar camadas finas e contratos de sucesso |

## Matriz de Cobertura dos Achados

| ID do achado | Severidade | Decisão | Etapas do plano | Validação | Risco residual |
|---|---|---|---|---|---|
| AP-02 | CRITICAL | FIX | P01 | seed sem senha literal; admin somente por configuração; testes de login | segredo configurado ainda deve ser gerenciado pelo operador |
| AP-03 | CRITICAL | FIX | P04 | 401 sem sessão, 403 por papel/ownership e sucesso autenticado | sessão/cookie exige `SECRET_KEY` estável e HTTPS em produção |
| AP-08 | HIGH | FIX | P04 | usuários/pedidos bloqueados anonimamente e limitados por papel/ownership | política de minimização/paginação poderá evoluir |
| AP-06A | MEDIUM | FIX | P02 | constraints, unicidade case-insensitive, FKs e testes de integridade | migração de base com duplicidades deve falhar para correção manual segura |
| AP-06B | MEDIUM | FIX | P01 | app factory sem DDL/seed padrão; comandos `init-db`/`seed-db` | operação deve executar os comandos antes do primeiro start |
| AP-14 | LOW | FIX | P03 | testes nos limites e constantes de domínio nomeadas | política continua estática, mas fica explícita |
| AP-15 | LOW | FIX | P02 | delete vira desativação; list/get/search ignoram inativos | não haverá endpoint de reativação nesta fase |

## Decisões Arquiteturais

| ID | Decisão | Motivo | Consequência |
|---|---|---|---|
| D01 | Manter a estrutura de diretórios MVC atual | ela já satisfaz dependências direcionais | nenhuma movida ampla ou reescrita |
| D02 | Usar sessão assinada nativa do Flask | evita nova dependência e integra-se ao tratamento atual | login passa a estabelecer sessão; produção requer segredo estável/HTTPS |
| D03 | Autorizar por papel e ownership | protege dados e mutações com regra explícita | respostas anônimas/indevidas passam a 401/403 intencionalmente |
| D04 | Preservar métodos e caminhos dos 19 endpoints | compatibilidade externa é prioridade | apenas pré-condições de segurança mudam nos endpoints protegidos |
| D05 | Separar schema e seed em comandos explícitos | remove efeito colateral do boot | README e preparação de testes precisam ser atualizados |
| D06 | Implementar soft delete de produto | dá sentido a `ativo` e preserva histórico | `DELETE` mantém resposta 200, mas atualiza `ativo=0` |
| D07 | Migrar schema SQLite de forma transacional e fail-fast | protege dados em vez de corrigir ambiguidades silenciosamente | duplicidades/integridade inválida exigem intervenção explícita |

## Etapas de Refatoração

### P01 - Configuração, inicialização e seed seguros

- Objetivo: remover credenciais literais e DDL/seed do boot padrão, registrar CLI explícita e configuração segura.
- Achados cobertos: AP-02, AP-06B.
- Arquivos esperados: `loja/config.py`, `loja/database.py`, `loja/__init__.py`, `tests/test_api.py`.
- Restrições: sem dependências novas; `python app.py` continua sendo o comando de servidor.
- Validação: comandos CLI em banco temporário, ausência das senhas auditadas e suíte existente.

### P02 - Integridade do schema e ciclo de vida do produto

- Objetivo: adicionar migração/constraints e implementar soft delete coerente.
- Achados cobertos: AP-06A, AP-15.
- Arquivos esperados: `loja/database.py`, repositories de produto/pedido/usuário, services e testes.
- Restrições: preservar IDs, histórico de pedidos e envelopes HTTP.
- Validação: testes de unicidade/FKs/soft delete e suíte existente.

### P03 - Política de desconto explícita

- Objetivo: substituir números mágicos por faixas nomeadas e testar fronteiras.
- Achados cobertos: AP-14.
- Arquivos esperados: `loja/services/report_service.py`, testes.
- Restrições: resultados atuais permanecem iguais.
- Validação: testes abaixo, nos limites e acima de cada faixa.

### P04 - Autenticação, autorização e proteção de dados

- Objetivo: adicionar middleware de sessão, guards por papel/ownership e restringir CORS.
- Achados cobertos: AP-03, AP-08.
- Arquivos esperados: `loja/config.py`, `loja/middlewares/auth.py`, views, controller/service de pedido, testes.
- Restrições: rotas públicas de catálogo, criação de usuário, login, raiz e health permanecem públicas; métodos/caminhos não mudam.
- Validação: matriz 200/201 autenticado, 401 anônimo, 403 papel/ownership e ausência de dados em respostas negadas.

### P05 - Documentação, limpeza e validação final

- Objetivo: atualizar operação, conferir imports/camadas e validar startup/endpoints.
- Achados cobertos: todos.
- Arquivos esperados: `README.md`, artefatos de relatório e eventuais ajustes mínimos.
- Restrições: sem ampliar o escopo funcional.
- Validação: suíte completa, CLI, inicialização controlada, fumaça HTTP e varredura arquitetural.

## Contrato dos Endpoints a Preservar

| Método | Caminho | Comportamento alvo | Validação |
|---|---|---|---|
| GET | `/` | público, 200 | smoke/teste |
| GET | `/health` | público e sanitizado, 200 | smoke/teste |
| GET | `/produtos` | público, lista ativos | teste |
| GET | `/produtos/busca` | público, busca parametrizada em ativos | teste |
| GET | `/produtos/<int:id>` | público, 200/404 | teste |
| POST | `/produtos` | admin, 201; 401/403 sem permissão | teste |
| PUT | `/produtos/<int:id>` | admin, 200; 401/403 sem permissão | teste |
| DELETE | `/produtos/<int:id>` | admin, 200 e soft delete | teste |
| GET | `/usuarios` | admin, 200; 401/403 sem permissão | teste |
| GET | `/usuarios/<int:id>` | próprio usuário/admin, 200; 401/403 | teste |
| POST | `/usuarios` | público, 201 | teste |
| POST | `/login` | público, 200 e estabelece sessão | teste |
| POST | `/pedidos` | usuário para si/admin, 201; 401/403 | teste |
| GET | `/pedidos` | admin, 200; 401/403 | teste |
| GET | `/pedidos/usuario/<int:usuario_id>` | próprio usuário/admin, 200; 401/403 | teste |
| PUT | `/pedidos/<int:pedido_id>/status` | admin, 200; 401/403 | teste |
| GET | `/relatorios/vendas` | admin, 200; 401/403 | teste |
| POST | `/admin/reset-db` | token administrativo existente, 200/403 | teste |
| POST | `/admin/query` | sempre recusado, 403 | teste |

## Controles de Risco

- Executar cada tarefa em banco temporário antes da próxima.
- Marcar tarefa no `STATE.md` antes/depois de editar.
- Preservar o contrato de sucesso; documentar 401/403 como mudança de segurança aprovada.
- Não adicionar dependência externa nem alterar `requirements.txt`.
- Migração deve usar transação e falhar diante de duplicidades em vez de descartar dados.
- Manter o endpoint administrativo de reset com o mecanismo de token já testado.
- Rodar a suíte completa após cada mudança que afete schema, autenticação ou rotas.
