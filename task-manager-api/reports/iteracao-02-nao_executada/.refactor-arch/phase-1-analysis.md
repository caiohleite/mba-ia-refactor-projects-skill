# Fase 1 — Análise do Projeto `task-manager-api` (iteração 02)

Data: 2026-07-12

Relatório de auditoria: `reports/iteracao-02/audit-project-3.md`.

## Escopo e exclusões

- Raiz analisada: diretório atual do projeto.
- Excluídos: `.git`, `.agents`, `.codex`, `venv`, caches, bancos SQLite locais, relatórios e artefatos gerados.
- Mudanças preexistentes: relatórios anteriores removidos e `reports/iteracao-01/` não versionado; ambos preservados.
- Arquivos-fonte Python relevantes analisados: 44, incluindo testes e arquivos `__init__.py`.
- Manifesto: `requirements.txt`; ponto de entrada: `app.py`; seed: `seed.py`; testes: `tests/test_api.py`.

## Stack detectada

- Linguagem: Python.
- Framework HTTP: Flask 3.0.0 (`requirements.txt:1`, `app.py:1-18`).
- Persistência: Flask-SQLAlchemy 3.1.1/SQLAlchemy 2.x com SQLite por padrão (`requirements.txt:2`, `config.py:18-20`, `database.py:1-3`).
- CORS: Flask-CORS 4.0.0 (`requirements.txt:3`, `app.py:2,17`).
- Autenticação: tokens assinados e temporizados com `itsdangerous`, dependência transitiva do Flask (`services/auth_service.py:1-43`).
- Hash de senhas: API do Werkzeug para novas senhas, com ponte de migração sob login para hashes MD5 legados (`models/user.py:21-31`, `services/auth_service.py:15-26`).
- Inicialização documentada: `pip install -r requirements.txt`, `python seed.py`, `python app.py` (`README.md:7-13`).

## Domínio e dados

Domínio inferido: gerenciamento de tarefas, usuários, categorias, prioridades, estados, prazos, busca e relatórios de produtividade.

Tabelas/modelos:

- `users` — `models/user.py:10-19`.
- `categories` — `models/category.py:4-11`.
- `tasks` — `models/task.py:4-20`, com relações para usuário e categoria.

## Arquitetura atual

Classificação: **MVC/em camadas adequado**, com alguns pontos residuais a auditar.

Responsabilidades reais:

- `routes/`: registra 22 contratos e aplica autenticação/autorização; delega imediatamente aos controllers.
- `controllers/`: adapta request/query string, chama services e serializa respostas; não acessa ORM.
- `services/`: contém validação, autorização contextual e regras dos casos de uso.
- `repositories/`: concentra SQLAlchemy, consultas agregadas, eager loading e transações.
- `models/`: representa entidades, relações e comportamento diretamente ligado às entidades.
- `schemas/`: centraliza validação, constantes e serialização segura.
- `middlewares/`: centraliza autenticação/autorização e respostas de erro.
- `app.py`: funciona como composition root/application factory.

A separação não é apenas nominal: rotas e controllers não importam `database`, não usam `db` nem `.query`; services não dependem de Flask. O projeto, portanto, já satisfaz o alvo MVC da skill. Permanecem candidatos de auditoria sem gravidade arquitetural equivalente ao legado: criação de tabelas ao construir/importar a aplicação, APIs legadas no script de seed, compatibilidade MD5 temporária, documentação desatualizada e módulos utilitários/serviço de notificação aparentemente sem consumidores.

## Pontos de entrada e fluxo

- `create_app()` configura Flask/CORS/SQLAlchemy, registra erros e Blueprints e retorna a aplicação (`app.py:11-37`).
- O módulo cria uma instância global para compatibilidade com `python app.py` e `seed.py` (`app.py:40-48`).
- `seed.py` recria dados de demonstração.
- `tests/test_api.py` cobre os 22 contratos, autenticação/autorização, DTOs seguros, validação, migração de hash legado e limites arquiteturais.

## Contrato HTTP detectado

| Método | Caminho | Finalidade | Origem |
|---|---|---|---|
| GET | `/` | metadados básicos | `app.py:30-32` |
| GET | `/health` | saúde da API | `app.py:26-28` |
| GET | `/tasks` | listar tarefas | `routes/task_routes.py:10-12` |
| POST | `/tasks` | criar tarefa | `routes/task_routes.py:20-23` |
| GET | `/tasks/<int:task_id>` | consultar tarefa | `routes/task_routes.py:15-17` |
| PUT | `/tasks/<int:task_id>` | atualizar tarefa | `routes/task_routes.py:26-29` |
| DELETE | `/tasks/<int:task_id>` | excluir tarefa | `routes/task_routes.py:32-35` |
| GET | `/tasks/search` | pesquisar/filtrar tarefas | `routes/task_routes.py:38-40` |
| GET | `/tasks/stats` | estatísticas de tarefas | `routes/task_routes.py:43-45` |
| GET | `/users` | listar usuários | `routes/user_routes.py:10-13` |
| POST | `/users` | criar usuário | `routes/user_routes.py:22-25` |
| GET | `/users/<int:user_id>` | consultar usuário | `routes/user_routes.py:16-19` |
| PUT | `/users/<int:user_id>` | atualizar usuário | `routes/user_routes.py:28-31` |
| DELETE | `/users/<int:user_id>` | excluir usuário | `routes/user_routes.py:34-37` |
| GET | `/users/<int:user_id>/tasks` | listar tarefas do usuário | `routes/user_routes.py:40-43` |
| POST | `/login` | autenticar usuário | `routes/user_routes.py:46-48` |
| GET | `/reports/summary` | relatório consolidado | `routes/report_routes.py:10-13` |
| GET | `/reports/user/<int:user_id>` | relatório individual | `routes/report_routes.py:16-19` |
| GET | `/categories` | listar categorias | `routes/category_routes.py:10-12` |
| POST | `/categories` | criar categoria | `routes/category_routes.py:15-18` |
| PUT | `/categories/<int:category_id>` | atualizar categoria | `routes/category_routes.py:21-24` |
| DELETE | `/categories/<int:category_id>` | excluir categoria | `routes/category_routes.py:27-30` |

## Resumo operacional

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:           Python
Framework:           Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependências:        Flask-CORS; Werkzeug/itsdangerous via Flask
Domínio:             Gerenciador de tarefas, usuários, categorias e relatórios
Arquitetura:         MVC/em camadas adequado; pontos residuais sem concentração de responsabilidades
Arquivos-fonte:      44 arquivos analisados
Tabelas do banco:    users, categories, tasks
================================
```
