# Fase 1 — Análise do Projeto `task-manager-api`

Data: 2026-07-12

Relatório de auditoria definido pelo desafio: `reports/audit-project-3.md`.

## Escopo e exclusões

- Raiz analisada: diretório atual do projeto.
- Excluídos: `.git`, `.agents`, `.codex`, `venv`, caches `__pycache__`, bancos SQLite locais, relatórios e artefatos gerados.
- Árvore de trabalho antes da análise: limpa (`git status --short` sem saída).
- Arquivos-fonte Python relevantes analisados: 15.
- Não há suíte de testes versionada.

## Stack detectada

- Linguagem: Python.
- Framework HTTP: Flask 3.0.0, evidenciado por `requirements.txt:1` e por `Flask`/`Blueprint` em `app.py:1-9` e `routes/*.py`.
- Persistência: Flask-SQLAlchemy 3.1.1 com SQLite (`requirements.txt:2`, `database.py:1-3`, `app.py:11-16`).
- Serialização/respostas: `jsonify` e métodos `to_dict`; Marshmallow está declarado, mas não é usado pelo código-fonte atual.
- Dependências adicionais: Flask-CORS, Requests e python-dotenv; Requests e python-dotenv não aparecem em uso no código atual.
- Inicialização documentada: `pip install -r requirements.txt`, `python seed.py`, `python app.py` (`README.md:5-13`).

## Domínio e dados

Domínio inferido: gerenciador de tarefas com usuários, categorias, prioridades, estados, prazos, busca e relatórios de produtividade.

Tabelas/modelos detectados:

- `users` — `models/user.py:5-14`.
- `categories` — `models/category.py:4-11`.
- `tasks` — `models/task.py:5-21`, com chaves estrangeiras para usuários e categorias.

O banco é criado automaticamente durante a importação/inicialização da aplicação (`app.py:30-31`) e o `seed.py` recria os dados de exemplo por exclusão e inserção (`seed.py:8-96`).

## Arquitetura atual

Classificação: **MVC parcial / aplicação em camadas nominal**.

Existem `models/`, `routes/`, `services/` e `utils/`, mas as responsabilidades reais permanecem concentradas nas rotas:

- `routes/task_routes.py` faz HTTP, validação, consulta, persistência, regra de atraso, serialização e estatísticas.
- `routes/user_routes.py` faz HTTP, autenticação, validação, persistência, exclusão em cascata manual e serialização.
- `routes/report_routes.py` mistura endpoints de relatórios e CRUD de categorias, além de consultas e agregações.
- `services/notification_service.py` é isolado, não é importado por nenhum fluxo da aplicação e mantém estado mutável em memória.
- Não há código-fonte versionado em `controllers/`, `repositories/`, `schemas/` ou `middlewares/`; há apenas caches Python excluídos da análise.

Portanto, os Blueprints atuam simultaneamente como View/Route, Controller, Service e Repository. A separação existente é insuficiente para MVC.

## Pontos de entrada e fluxo

- `app.py`: cria e configura a aplicação, inicializa extensões, registra Blueprints, cria tabelas e inicia o servidor de desenvolvimento.
- `seed.py`: importa a aplicação, apaga dados das três entidades e insere dados de demonstração.
- `database.py`: expõe a instância global de `SQLAlchemy`.

## Contrato HTTP detectado

| Método | Caminho | Finalidade | Origem |
|---|---|---|---|
| GET | `/` | metadados básicos da API | `app.py:26-28` |
| GET | `/health` | status e timestamp | `app.py:22-24` |
| GET | `/tasks` | listar tarefas | `routes/task_routes.py:11-63` |
| POST | `/tasks` | criar tarefa | `routes/task_routes.py:85-154` |
| GET | `/tasks/<int:task_id>` | consultar tarefa | `routes/task_routes.py:65-83` |
| PUT | `/tasks/<int:task_id>` | atualizar tarefa | `routes/task_routes.py:156-223` |
| DELETE | `/tasks/<int:task_id>` | excluir tarefa | `routes/task_routes.py:225-238` |
| GET | `/tasks/search` | pesquisar/filtrar tarefas | `routes/task_routes.py:240-271` |
| GET | `/tasks/stats` | estatísticas de tarefas | `routes/task_routes.py:273-299` |
| GET | `/users` | listar usuários | `routes/user_routes.py:10-25` |
| POST | `/users` | criar usuário | `routes/user_routes.py:42-90` |
| GET | `/users/<int:user_id>` | consultar usuário e tarefas | `routes/user_routes.py:27-40` |
| PUT | `/users/<int:user_id>` | atualizar usuário | `routes/user_routes.py:92-132` |
| DELETE | `/users/<int:user_id>` | excluir usuário e suas tarefas | `routes/user_routes.py:134-151` |
| GET | `/users/<int:user_id>/tasks` | listar tarefas do usuário | `routes/user_routes.py:153-183` |
| POST | `/login` | autenticar usuário | `routes/user_routes.py:185-211` |
| GET | `/reports/summary` | relatório consolidado | `routes/report_routes.py:12-101` |
| GET | `/reports/user/<int:user_id>` | relatório individual | `routes/report_routes.py:103-155` |
| GET | `/categories` | listar categorias | `routes/report_routes.py:157-165` |
| POST | `/categories` | criar categoria | `routes/report_routes.py:167-188` |
| PUT | `/categories/<int:cat_id>` | atualizar categoria | `routes/report_routes.py:190-209` |
| DELETE | `/categories/<int:cat_id>` | excluir categoria | `routes/report_routes.py:211-223` |

## Sinais encaminhados para a auditoria

- Credenciais e segredo fixos no código.
- Hash de senha MD5 e inclusão do hash nas respostas.
- Token de login falso e previsível; ausência de proteção de endpoints.
- Rotas grandes com acesso direto ao ORM e regras de negócio.
- Potenciais consultas N+1.
- Uso de `Query.get`, API legada no SQLAlchemy 2.x.
- Capturas genéricas ou nuas de exceção.
- Configuração e efeitos colaterais na importação da aplicação.
- Duplicação de validação, serialização e cálculo de atraso.
- Ausência de testes automatizados.

## Resumo operacional

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:           Python
Framework:           Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependências:        Flask-CORS, Marshmallow, Requests, python-dotenv
Domínio:             Gerenciador de tarefas, usuários, categorias e relatórios
Arquitetura:         MVC parcial; Blueprints concentram HTTP, regras, persistência e serialização
Arquivos-fonte:      15 arquivos analisados
Tabelas do banco:    users, categories, tasks
================================
```
