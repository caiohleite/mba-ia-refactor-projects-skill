# Analise De Projeto

Use este guia na Fase 1 para entender a codebase antes de auditar ou refatorar. A analise deve ser agnostica de tecnologia: detectar fatos a partir de arquivos, manifests, imports, rotas, inicializacao, modelos e uso real das dependencias.

## Escopo E Inventario

1. Definir o diretorio raiz do projeto.
2. Ignorar `.git`, caches, ambientes virtuais, `node_modules`, `dist`, `build`, bancos locais gerados e relatorios antigos, salvo quando o usuario pedir o contrario.
3. Listar manifests e lockfiles: `package.json`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`, `go.mod`, `pom.xml`, `build.gradle`, `composer.json`.
4. Listar entry points: `app.py`, `main.py`, `wsgi.py`, `src/app.js`, `server.js`, `index.js`, CLIs, Dockerfiles e scripts de start.
5. Listar arquivos de dominio: models, routes, controllers, services, repositories, schemas, migrations, seeders, utils e middlewares.
6. Contar somente arquivos de codigo relevantes para o resumo. Excluir documentacao e artefatos gerados.

## Deteccao De Linguagem E Framework

| Evidencia | Linguagem/framework provavel |
|---|---|
| `requirements.txt` com `flask`, imports `from flask import` | Python + Flask |
| `flask_sqlalchemy`, `SQLAlchemy()` | Flask + SQLAlchemy |
| `sqlite3.connect`, arquivos `.db`, `CREATE TABLE` inline | SQLite direto |
| `package.json` com `express`, `const express = require` | Node.js + Express |
| `app.use(express.json())`, `app.get/post/put/delete` | API HTTP Express |
| `sequelize`, `typeorm`, `prisma`, `mongoose` | ORM/ODM Node.js |
| `FastAPI()`, `APIRouter` | Python + FastAPI |
| `Django`, `settings.py`, `urls.py` | Python + Django |

Quando houver mais de uma stack, relatar cada uma e delimitar o escopo analisado.

## Deteccao De Banco De Dados

Procure por:

- chamadas diretas de conexao (`sqlite3.connect`, `new sqlite3.Database`, `psycopg2.connect`, `mysql.createConnection`);
- ORMs (`SQLAlchemy`, `Sequelize`, `Prisma`, `TypeORM`, `Mongoose`);
- migrations, schemas, seeds e arquivos `.sql`;
- strings de conexao hardcoded ou lidas de ambiente;
- tabelas criadas em runtime e models declarativos.

No resumo, listar tabelas ou entidades de dominio detectadas, por exemplo `produtos`, `usuarios`, `pedidos`, `tasks`, `categories`.

## Mapeamento Arquitetural

Classificar a arquitetura real a partir do comportamento dos arquivos:

- **Monolito procedural**: entry point registra rotas e chama funcoes globais; persistencia e regra de negocio misturadas.
- **God object/god file**: uma classe ou arquivo concentra bootstrap, rotas, validacao, regras, SQL e integracoes.
- **MVC parcial**: existem pastas como `models/` e `routes/`, mas routes fazem regra de negocio, queries, serializacao complexa ou chamadas externas.
- **MVC/layered adequado**: routes finas, controllers coordenam casos de uso, models/repositories isolam persistencia e services guardam regra de negocio.

Nao confiar apenas em nomes de diretorios. Confirmar responsabilidades lendo chamadas, imports e fluxo de dados.

## Inferencia De Dominio

Inferir o dominio pelos nomes de entidades, rotas, seeds e mensagens:

- E-commerce: produtos, usuarios, pedidos, itens, estoque, relatorios de vendas.
- LMS/checkout: users, courses, enrollments, payments, checkout, financial reports.
- Task Manager: tasks, users, categories, priorities, overdue, reports.

Declarar a inferencia como `Domain` no resumo e citar evidencias no relatorio se houver incerteza.

## Sinais De Arquitetura Problematicos

Registrar para a Fase 2 quando encontrar:

- rotas manipulando banco diretamente;
- controllers com validacao longa, regra de negocio, notificacoes ou queries;
- models expondo senhas, tokens ou detalhes internos na serializacao;
- SQL concatenado com input;
- chamadas N+1 em loops;
- configuracao sensivel no codigo;
- estado global mutavel;
- endpoints administrativos sem autenticacao;
- tratamento de erro generico que esconde falhas ou vaza excecoes;
- APIs deprecated ou legadas.

## Resumo Da Fase 1

Produzir o resumo operacional com:

- linguagem e framework;
- principais dependencias;
- dominio;
- arquitetura atual;
- numero de arquivos analisados;
- tabelas, modelos ou colecoes detectadas;
- observacoes de incerteza quando aplicavel.
