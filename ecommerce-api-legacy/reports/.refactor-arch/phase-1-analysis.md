# Fase 1 - Análise do Projeto ecommerce-api-legacy

**Gerado em**: 2026-07-11 20:32:22 -0300  
**Escopo**: `.`  
**Exclusões**: `.git`, `node_modules`, `vendor`, caches, artefatos gerados e `reports`

## Inventário

- Manifestos: `package.json`, `package-lock.json`.
- Ponto de entrada: `src/app.js`.
- Código-fonte: `src/app.js`, `src/AppManager.js`, `src/utils.js` (3 arquivos, aproximadamente 180 LOC).
- Contratos/requisições documentadas: `api.http`.
- Documentação de execução: `README.md`.
- Testes automatizados, migrations, schemas, controllers, services, repositories e middlewares: não encontrados.

## Stack detectada

- Linguagem: JavaScript (CommonJS) sobre Node.js.
- Framework HTTP: Express, declarado como `^4.18.2`; lockfile resolve `4.22.1`.
- Banco: SQLite em memória por `sqlite3`, declarado como `^5.1.6`; lockfile resolve `5.1.7`.
- Inicialização documentada: `npm install` e `npm start`.
- URL local documentada: `http://localhost:3000`.
- Restrição desta análise: o executável `node` não está disponível no ambiente atual, portanto a aplicação não foi inicializada na Fase 1.

## Domínio inferido

LMS com fluxo de checkout. As evidências são as entidades `users`, `courses`, `enrollments`, `payments` e `audit_logs`, além das rotas de checkout e relatório financeiro. O sistema cria usuários, processa uma simulação de pagamento, matricula alunos e consolida receita por curso.

## Persistência e entidades

O banco SQLite `:memory:` é criado no construtor de `AppManager` (`src/AppManager.js:5-8`). O schema e os seeds são criados na inicialização (`src/AppManager.js:10-23`). Tabelas detectadas:

- `users`: usuário, e-mail e senha.
- `courses`: curso, preço e indicador de atividade.
- `enrollments`: associação usuário-curso.
- `payments`: pagamento associado à matrícula.
- `audit_logs`: ações e data de criação.

Não há constraints de chave estrangeira declaradas nem migrations versionadas.

## Arquitetura atual

Monolito com Objeto Deus. `src/app.js` apenas compõe Express e instancia `AppManager`, enquanto `src/AppManager.js` concentra ciclo de vida do banco, schema, seeds, registro das três rotas, validação HTTP, regras de checkout, acesso SQL, transações implícitas, relatório, serialização e respostas de erro. `src/utils.js` mistura configuração, estado global, logging/cache e hashing de senha.

Não existem camadas MVC reais. As funções de rota exercem simultaneamente papéis de View/Route, Controller, Service e Repository/Model.

## Contrato HTTP detectado

| Método | Caminho | Entrada principal | Saída observada |
|---|---|---|---|
| POST | `/api/checkout` | JSON `usr`, `eml`, `pwd`, `c_id`, `card` | `200` JSON `{ msg, enrollment_id }`; erros `400`, `404` ou `500` em texto |
| GET | `/api/admin/financial-report` | sem payload | JSON com itens `{ course, revenue, students[] }` |
| DELETE | `/api/users/:id` | parâmetro de caminho `id` | texto confirmando exclusão e dados relacionados órfãos |

## Fluxos principais

- Boot: cria Express, habilita JSON, abre SQLite em memória, agenda criação/seeds, registra rotas e começa a escutar a porta 3000.
- Checkout: valida parcialmente o corpo, busca curso e usuário, cria o usuário quando ausente, simula pagamento pelo prefixo do cartão, cria matrícula/pagamento/log e responde.
- Relatório: busca cursos, depois matrículas, usuários e pagamentos em consultas aninhadas.
- Exclusão: remove somente o usuário, sem tratar erro ou integridade referencial.

## Riscos macro encaminhados à auditoria

- credenciais e chave de pagamento fixadas no código;
- senha seed em texto puro e algoritmo caseiro baseado em Base64;
- cartão e chave de pagamento escritos integralmente em log;
- endpoints sensíveis sem autenticação/autorização;
- regras, HTTP e persistência concentrados no mesmo arquivo/classe;
- escrita de checkout sem transação e exclusão gerando dados órfãos;
- padrão N+1 no relatório financeiro;
- estado global mutável;
- validação e tratamento de erros incompletos/inconsistentes;
- nomes obscuros, strings e valores mágicos.

## Resumo operacional

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:           JavaScript (Node.js/CommonJS)
Framework:           Express 4.22.1
Dependências:        express, sqlite3 5.1.7
Domínio:             LMS com checkout, matrículas e pagamentos
Arquitetura:         monolito com Objeto Deus; HTTP, regras e SQL misturados
Arquivos-fonte:      3 arquivos analisados
Tabelas do banco:    users, courses, enrollments, payments, audit_logs
================================
```
