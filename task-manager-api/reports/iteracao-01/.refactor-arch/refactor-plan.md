# Plano de Refatoração MVC - task-manager-api

## Entradas

- Relatório de auditoria: `reports/audit-project-3.md`.
- Arquivo de estado: `reports/.refactor-arch/STATE.md`.
- Aprovado em: 2026-07-12, pela resposta explícita `s` do usuário.
- Árvore de trabalho: código-fonte limpo; somente os artefatos novos de `reports/` estão presentes.

## Arquitetura Alvo

A aplicação manterá Flask, SQLAlchemy, os comandos `python app.py`/`python seed.py` e os 22 métodos/caminhos HTTP. `app.py` será a raiz de composição/application factory; `routes/` apenas registrará endpoints; `controllers/` adaptará HTTP; `services/` executará casos de uso; `repositories/` encapsulará SQLAlchemy; `models/` representará dados e invariantes; `schemas/` concentrará validação e DTOs; `middlewares/` tratará autenticação, autorização e erros.

## Mapeamento de Camadas

| Responsabilidade atual | Arquivos atuais | Camada alvo | Arquivos alvo | Justificativa |
|---|---|---|---|---|
| configuração, extensão, registro e boot | `app.py`, `database.py` | configuração/composição | `config.py`, `app.py`, `database.py` | eliminar segredos e efeito arquitetural disperso |
| dados e hashes | `models/*.py` | models | `models/*.py` | manter ORM e invariantes; retirar DTO sensível |
| queries/transações | `routes/*.py` | repositories | `repositories/{task,user,category,report}_repository.py` | remover ORM das camadas HTTP e N+1 |
| validação/serialização | rotas, models, `utils/helpers.py` | schemas/DTOs | `schemas/constants.py`, `validators.py`, `serializers.py` | fonte única e DTO público seguro |
| regras/casos de uso | `routes/*.py` | services | `services/{task,user,auth,category,report}_service.py` | testar regras sem Flask |
| adaptação HTTP | handlers em `routes/*.py` | controllers | `controllers/{task,user,category,report}_controller.py` | converter request/resultado/status |
| registro dos endpoints | decorators e lógica em `routes/*.py` | views/routes | `routes/*.py` + novo `category_routes.py` | Blueprints finos e coesos por domínio |
| autenticação e erros | ausente/disperso | middlewares | `middlewares/auth.py`, `error_handler.py` | segurança e erros centralizados |
| integração SMTP | credenciais em `notification_service.py` | service configurável | `services/notification_service.py` | remover segredos e estado residual |

## Matriz de Cobertura dos Achados

| ID do achado | Severidade | Decisão | Etapas do plano | Validação | Risco residual |
|---|---|---|---|---|---|
| AP-02 | CRITICAL | FIX | P01, P05 | busca por segredos; boot com configuração padrão/ambiente | chave aleatória invalida tokens após restart se `SECRET_KEY` não for configurada |
| AP-03 | CRITICAL | FIX | P03, P04 | 401 sem token, 403 sem papel, sucesso com token/papel | clientes precisarão enviar Bearer token nas rotas protegidas |
| AP-07 | CRITICAL | FIX | P02, P03 | hash Werkzeug; login/token assinado; migração MD5 no login | hashes MD5 só são migrados quando o usuário autentica |
| AP-08 | CRITICAL | FIX | P02, P04 | respostas não contêm `password` | remoção intencional do campo inseguro altera resposta legada |
| AP-04 | HIGH | FIX | P02-P05 | inspeção de dependências e tamanho/responsabilidade das rotas | controllers ainda conhecem Flask, conforme MVC adotado |
| AP-05 | HIGH | FIX | P03, P04 | testes de services e varredura de rotas | regras simples de adaptação permanecem em controllers |
| AP-06 | HIGH | FIX | P02-P04 | ausência de `db`/`.query` em routes/controllers | services coordenam commits via repositories |
| AP-09 | MEDIUM | FIX | P02 | eager loading/agregações e inspeção de queries em loops | relatórios ainda executam poucas queries agregadas separadas |
| AP-11 | MEDIUM | FIX | P02, P03 | testes de payload inválido e constantes únicas | mensagens históricas serão preservadas quando relevante |
| AP-12 | MEDIUM | FIX | P01, P04 | handler central e respostas JSON padronizadas | erros inesperados seguem como 500 genérico |
| AP-13 | MEDIUM | FIX | P01, P02 | busca por `query.get`/`utcnow` | datas persistem sem timezone no SQLite por compatibilidade, geradas a partir de UTC explícito |
| AP-14 | LOW | FIX | P02-P05 | revisão estática | nomes de colunas/JSON públicos não mudam |
| AP-15 | LOW | FIX | P05 | busca de imports/resíduos e boot | dependências declaradas não serão removidas do manifesto sem necessidade operacional |

## Decisões Arquiteturais

| ID | Decisão | Motivo | Consequência |
|---|---|---|---|
| DA-01 | manter estrutura de pacotes na raiz em vez de criar `src/` | reduz risco de import e preserva comandos atuais | MVC será expresso pelos pacotes existentes |
| DA-02 | usar application factory e manter `app = create_app()` | facilita testes sem quebrar `python app.py` e `seed.py` | import de `app` ainda cria a aplicação padrão |
| DA-03 | usar `itsdangerous`/Werkzeug já transitivos do Flask | evita nova dependência para token e senha | tokens dependem da `SECRET_KEY` e têm validade configurável |
| DA-04 | aceitar hashes MD5 existentes apenas para migração no login | preserva usuários do banco atual | suporte legado temporário fica isolado no model/service |
| DA-05 | proteger mutações privilegiadas e relatórios | corrige AP-03 conforme auditoria aprovada | contratos de autenticação mudam intencionalmente, sem mudar métodos/caminhos |
| DA-06 | manter nomes e campos não sensíveis das respostas | maximiza compatibilidade | somente `password` será removido por segurança |
| DA-07 | usar UTC explícito convertido para datetime ingênuo no SQLite | evita comparação aware/naive e moderniza a origem do tempo | timezone não fica armazenado no schema legado |

## Etapas de Refatoração

### P01 - Configuração, tempo e erros
- Objetivo: extrair ambiente, introduzir application settings, relógio UTC e exceções/handler central.
- Achados cobertos: AP-02, AP-12, AP-13.
- Arquivos esperados: `config.py`, `utils/time.py`, `exceptions.py`, `middlewares/error_handler.py`.
- Restrições: nenhuma dependência nova; não mudar caminhos HTTP.
- Validação: parse AST e teste unitário do handler/configuração.

### P02 - Models, DTOs e repositories
- Objetivo: proteger senha, centralizar validação/serialização e encapsular queries com eager loading/agregações.
- Achados cobertos: AP-04, AP-06, AP-07, AP-08, AP-09, AP-11, AP-13, AP-14.
- Arquivos esperados: `models/*.py`, `schemas/*.py`, `repositories/*.py`.
- Restrições: manter tabelas/colunas e formatos públicos não sensíveis.
- Validação: testes de hash/DTO/validator e busca estática por API legada.

### P03 - Services e segurança
- Objetivo: extrair casos de uso, transações, autenticação assinada e autorização.
- Achados cobertos: AP-03, AP-05, AP-06, AP-07, AP-11.
- Arquivos esperados: `services/*.py`, `middlewares/auth.py`.
- Restrições: login público; registro público cria somente papel `user`; ações privilegiadas exigem papel.
- Validação: testes diretos e HTTP de login, 401, 403 e sucesso autorizado.

### P04 - Controllers e rotas finas
- Objetivo: mover adaptação HTTP para controllers e reduzir Blueprints a registro/delegação.
- Achados cobertos: AP-03, AP-04, AP-05, AP-06, AP-08, AP-12.
- Arquivos esperados: `controllers/*.py`, `routes/*.py`.
- Restrições: preservar os 22 métodos/caminhos e status de sucesso/erros de domínio quando não afetados pela segurança.
- Validação: mapa de URL e smoke tests de todos os endpoints.

### P05 - Composição e limpeza
- Objetivo: registrar camadas/middlewares, configurar SMTP e remover imports/resíduos ativos.
- Achados cobertos: AP-02, AP-04, AP-14, AP-15.
- Arquivos esperados: `app.py`, `services/notification_service.py`, `utils/helpers.py`, `seed.py`.
- Restrições: preservar `python app.py`, `python seed.py`, host/porta configuráveis.
- Validação: boot controlado, parse AST e varredura por segredos/imports suspeitos.

### P06 - Regressão automatizada e validação final
- Objetivo: criar testes de contrato e validar boot, endpoints e arquitetura.
- Achados cobertos: todos os AP-02 a AP-15 aprovados.
- Arquivos esperados: `tests/test_api.py`, `reports/.refactor-arch/validation-report.md`.
- Restrições: banco em memória/temporário; não destruir `instance/tasks.db`.
- Validação: `venv/bin/python -m unittest discover -s tests -v`, boot e smoke tests.

## Contrato dos Endpoints a Preservar

| Métodos | Caminhos | Comportamento preservado | Validação |
|---|---|---|---|
| GET | `/`, `/health` | metadados e saúde | HTTP 200 e chaves existentes |
| GET/POST | `/tasks` | listar/criar tarefas | payload/status; POST autenticado |
| GET/PUT/DELETE | `/tasks/<int:task_id>` | consultar/alterar/excluir | GET público; mutações autenticadas |
| GET | `/tasks/search`, `/tasks/stats` | busca e estatísticas | campos e filtros existentes |
| GET/POST | `/users` | listar/criar | GET autenticado; registro público sem autoelevação |
| GET/PUT/DELETE | `/users/<int:user_id>` | consultar/alterar/excluir | autenticação; DELETE/admin; sem campo `password` |
| GET | `/users/<int:user_id>/tasks` | tarefas do usuário | próprio usuário ou papel elevado |
| POST | `/login` | autenticação | mesmas credenciais; token real assinado; sem hash na resposta |
| GET | `/reports/summary`, `/reports/user/<int:user_id>` | relatórios | autenticação/autorização e campos existentes |
| GET/POST | `/categories` | listar/criar | GET público; POST/admin |
| PUT/DELETE | `/categories/<int:cat_id>` | alterar/excluir | admin obrigatório |

O detalhamento individual dos 22 endpoints permanece em `STATE.md`.

## Controles de Risco

- Usar banco SQLite em memória nos testes; não executar seed destrutivo sobre o banco do usuário.
- Manter compatibilidade de hashes MD5 apenas como caminho de migração, regravando hash forte após login válido.
- Validar cada pacote por AST/import antes de conectar a próxima camada.
- Atualizar `STATE.md` antes e depois de cada tarefa.
- Não adicionar dependências nem alterar schema do banco.
- Registrar explicitamente as duas mudanças de contrato aprovadas por segurança: Bearer token nas rotas protegidas e ausência de `password` em respostas.
