# Fase 1 — Análise do Projeto

## Escopo e inventário

- Projeto: `ecommerce-api-legacy`
- Código analisado: 28 arquivos JavaScript relevantes (27 em `src/` e 1 suíte em `test/`).
- Manifestos e contratos adicionais: `package.json`, `package-lock.json`, `README.md` e `api.http`.
- Exclusões: `.git`, `node_modules`, dependências vendorizadas, caches, artefatos gerados, bancos locais e `reports`.
- Ponto de entrada: `src/server.js`; comando declarado: `npm start` (`node src/server.js`).
- Testes: `npm test` (`node test/run.js`).

## Stack detectada

- Linguagem: JavaScript CommonJS para Node.js.
- Framework HTTP: Express 4 (`package.json:11`, `src/app.js:1-24`).
- Banco: SQLite em memória por meio de `sqlite3` (`package.json:12`, `src/db/connection.js:1-22`).
- Dependências de produção: `express` e `sqlite3`.
- Criptografia: módulo nativo `node:crypto`, com `scrypt`, salt aleatório e comparação de tempo constante (`src/services/passwordService.js:1-35`).
- Injeção de dependências: composição explícita em `src/server.js:21-49`.

## Domínio e persistência

O domínio é um LMS com checkout de cursos, matrículas, pagamentos, relatório financeiro e administração de usuários. A inferência é sustentada pelos endpoints, serviços e schema.

Tabelas definidas em `src/db/initialize.js:3-41`:

- `users`
- `courses`
- `enrollments`
- `payments`
- `audit_logs`

O banco é recriado e populado em memória a cada inicialização (`src/server.js:23-27`, `src/db/initialize.js:43-74`).

## Arquitetura real

Classificação: **MVC/em camadas adequado**, com repository e service layers complementares.

- **View/Routes**: as rotas somente declaram método, caminho, middleware e controller (`src/routes/*.js`).
- **Controllers**: adaptam entrada/saída HTTP, validam parâmetros e delegam casos de uso (`src/controllers/*.js`).
- **Services**: concentram regras e orquestração de checkout, relatório e exclusão (`src/services/*.js`).
- **Models/Persistência**: como o projeto não usa ORM, repositories e helpers SQLite cumprem a responsabilidade de acesso e representação persistente (`src/repositories/*.js`, `src/db/*.js`).
- **Middlewares**: autenticação administrativa e tratamento uniforme de erros estão isolados (`src/middlewares/*.js`).
- **Composition root**: criação do banco e montagem das dependências ficam em `src/server.js`.

Não foram observados SQL em routes/controllers, objeto Deus, estado global mutável, credenciais fixas ou mistura significativa de HTTP com persistência. A nomenclatura e as responsabilidades efetivas estão alinhadas.

## Contrato HTTP detectado

| Método | Caminho | Finalidade | Proteção | Respostas principais |
|---|---|---|---|---|
| POST | `/api/checkout` | Criar usuário quando necessário, matrícula, pagamento e auditoria | Pública | 200 sucesso; 400 payload/pagamento; 404 curso |
| GET | `/api/admin/financial-report` | Consolidar receita e alunos por curso | `x-admin-api-key` | 200; 401; 503 sem configuração |
| DELETE | `/api/users/:id` | Excluir usuário e dependências por cascata | `x-admin-api-key` | 200; 400; 401; 503 sem configuração |

## Sinais encaminhados à auditoria

- A arquitetura já está materialmente em MVC; a Fase 2 deve determinar se qualquer refatoração adicional é necessária.
- O checkout usa uma regra simulada de autorização baseada no primeiro dígito do cartão; é preciso distinguir dívida funcional deliberada de antipadrão arquitetural (`src/services/checkoutService.js:34-40`).
- O payload contém o número integral do cartão em memória durante a requisição, embora ele não seja persistido nem registrado (`src/validators/checkoutValidator.js:15-32`).
- A exclusão retorna sucesso sem distinguir usuário inexistente (`src/services/userService.js:6-9`, `src/repositories/userRepository.js:22-24`).
- A validação executável precisa considerar que o ambiente atual não encontra um runtime Node.js utilizável.

## Resumo operacional

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:           JavaScript (Node.js, CommonJS)
Framework:           Express 4
Dependências:        express, sqlite3; node:crypto
Domínio:             LMS/e-commerce de cursos com checkout e relatórios
Arquitetura:         MVC em camadas adequado, com services e repositories
Arquivos-fonte:      28 arquivos analisados (27 aplicação + 1 teste)
Tabelas do banco:    users, courses, enrollments, payments, audit_logs
================================
```
