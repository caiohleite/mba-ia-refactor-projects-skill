# Análise de Projeto

Use este guia na Fase 1 para entender a base de código antes de auditar ou refatorar. A análise deve ser agnóstica de tecnologia: detectar fatos a partir de arquivos, arquivos de manifesto, importações, rotas, inicialização, modelos e uso real das dependências.

## Escopo e Inventário

1. Definir o diretório raiz do projeto.
2. Ignorar `.git`, caches, ambientes virtuais, `node_modules`, `dist`, `build`, bancos locais gerados e relatórios antigos, salvo quando o usuário pedir o contrário.
3. Listar arquivos de manifesto e lockfiles: `package.json`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`, `go.mod`, `pom.xml`, `build.gradle`, `composer.json`.
4. Listar pontos de entrada: `app.py`, `main.py`, `wsgi.py`, `src/app.js`, `server.js`, `index.js`, CLIs, Dockerfiles e scripts de inicialização.
5. Listar arquivos de domínio: models, routes, controllers, services, repositories, schemas, migrations, seeders, utils e middlewares.
6. Contar somente arquivos de código relevantes para o resumo. Excluir documentação e artefatos gerados.

## Detecção de Linguagem e Framework

| Evidência | Linguagem/framework provável |
|---|---|
| `requirements.txt` com `flask`, imports `from flask import` | Python + Flask |
| `flask_sqlalchemy`, `SQLAlchemy()` | Flask + SQLAlchemy |
| `sqlite3.connect`, arquivos `.db`, `CREATE TABLE` embutido | SQLite direto |
| `package.json` com `express`, `const express = require` | Node.js + Express |
| `app.use(express.json())`, `app.get/post/put/delete` | API HTTP Express |
| `sequelize`, `typeorm`, `prisma`, `mongoose` | ORM/ODM Node.js |
| `FastAPI()`, `APIRouter` | Python + FastAPI |
| `Django`, `settings.py`, `urls.py` | Python + Django |

Quando houver mais de uma stack, relatar cada uma e delimitar o escopo analisado.

## Detecção de Banco de Dados

Procure por:

- chamadas diretas de conexão (`sqlite3.connect`, `new sqlite3.Database`, `psycopg2.connect`, `mysql.createConnection`);
- ORMs (`SQLAlchemy`, `Sequelize`, `Prisma`, `TypeORM`, `Mongoose`);
- migrações, schemas, seeds e arquivos `.sql`;
- strings de conexão fixadas no código ou lidas de ambiente;
- tabelas criadas em tempo de execução e models declarativos.

No resumo, listar tabelas ou entidades de domínio detectadas, por exemplo `produtos`, `usuarios`, `pedidos`, `tasks`, `categories`.

## Mapeamento Arquitetural

Classificar a arquitetura real a partir do comportamento dos arquivos:

- **Monolito procedural**: ponto de entrada registra rotas e chama funções globais; persistência e regra de negócio misturadas.
- **Objeto Deus/arquivo Deus**: uma classe ou arquivo concentra inicialização, rotas, validação, regras, SQL e integrações.
- **MVC parcial**: existem pastas como `models/` e `routes/`, mas routes fazem regra de negócio, consultas, serialização complexa ou chamadas externas.
- **MVC/em camadas adequado**: routes finas, controllers coordenam casos de uso, models/repositories isolam persistência e services guardam regra de negócio.

Não confiar apenas em nomes de diretórios. Confirmar responsabilidades lendo chamadas, imports e fluxo de dados.

## Inferência de Domínio

Inferir o domínio pelos nomes de entidades, rotas, seeds e mensagens:

- E-commerce: produtos, usuarios, pedidos, itens, estoque, relatorios de vendas.
- LMS/checkout: usuários, cursos, matrículas, pagamentos, checkout e relatórios financeiros.
- Gerenciador de tarefas: tarefas, usuários, categorias, prioridades, atrasos e relatórios.

Declarar a inferência como `Domínio` no resumo e citar evidências no relatório se houver incerteza.

## Sinais de Arquitetura Problemáticos

Registrar para a Fase 2 quando encontrar:

- rotas manipulando banco diretamente;
- controllers com validação longa, regra de negócio, notificações ou consultas;
- models expondo senhas, tokens ou detalhes internos na serialização;
- SQL concatenado com entrada externa;
- chamadas N+1 em loops;
- configuração sensível no código;
- estado global mutável;
- endpoints administrativos sem autenticação;
- tratamento de erro genérico que esconde falhas ou vaza exceções;
- APIs obsoletas ou legadas.

## Resumo da Fase 1

Produzir o resumo operacional com:

- linguagem e framework;
- principais dependências;
- domínio;
- arquitetura atual;
- número de arquivos analisados;
- tabelas, modelos ou coleções detectadas;
- observações de incerteza quando aplicável.
