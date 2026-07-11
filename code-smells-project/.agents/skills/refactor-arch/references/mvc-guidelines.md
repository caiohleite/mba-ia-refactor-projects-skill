# Diretrizes de Arquitetura MVC

Use estas regras na Fase 3 para definir a arquitetura alvo. O objetivo não é impor uma estrutura idêntica para todas as tecnologias, mas preservar o mesmo contrato de responsabilidades.

## Responsabilidades

| Camada | Responsabilidade | Não deve conter |
|---|---|---|
| Config | Ler ambiente, defaults seguros, flags e conexões externas | Segredos hardcoded, regras de negócio |
| Models | Entidades, schemas, mapeamento ORM, invariantes simples | HTTP request/response, queries de relatório complexas, logs externos |
| Repositories/Data Access | Consultas, comandos de persistência e transações simples | Regras de checkout, notificações, serialização HTTP |
| Services/Use Cases | Regras de negócio, orquestração de domínio, transações compostas | Detalhes de Flask/Express, formato de resposta HTTP |
| Controllers | Coordenar caso de uso, converter erros de domínio em status, escolher DTO | SQL direto, regra de negócio pesada, chamadas externas soltas |
| Views/Routes | Definir rotas, extrair input HTTP, chamar controller, devolver resposta | Cálculo de domínio, acesso direto a banco, validação longa duplicada |
| Middlewares | Erros, auth, logging, CORS, request context | Regras de domínio |
| App/Composition Root | Criar app, registrar rotas, configurar dependências e iniciar servidor | Handlers de negócio ou queries |

## Estrutura Recomendada para Flask

```text
src/
|-- app.py
|-- config/
|   `-- settings.py
|-- models/
|   |-- user.py
|   `-- task.py
|-- repositories/
|   `-- task_repository.py
|-- services/
|   `-- task_service.py
|-- controllers/
|   `-- task_controller.py
|-- views/
|   `-- task_routes.py
|-- middlewares/
|   `-- error_handler.py
`-- extensions.py
```

Variações aceitáveis:

- usar `routes/` no lugar de `views/` quando o framework ou projeto já usa esse nome;
- manter `database.py` se ele for apenas extension/composition de banco;
- usar blueprints por domínio.

## Estrutura Recomendada para Express

```text
src/
|-- app.js
|-- server.js
|-- config/
|   `-- index.js
|-- models/
|   `-- user.js
|-- repositories/
|   `-- userRepository.js
|-- services/
|   `-- checkoutService.js
|-- controllers/
|   `-- checkoutController.js
|-- routes/
|   `-- checkoutRoutes.js
|-- middlewares/
|   `-- errorHandler.js
`-- db/
    `-- connection.js
```

Variações aceitáveis:

- manter CommonJS se o projeto já usa `require`;
- separar `app.js` (configura express) de `server.js` (listen);
- encapsular SQLite callbacks em repositories antes de converter para Promises, se a mudança menor reduzir risco.

## Princípios de Refatoração

- Preservar contrato externo primeiro; melhorar internals depois.
- Preferir pequenas movidas com imports ajustados a reescritas amplas.
- Manter nomes de domínio em português/inglês conforme o projeto já usa.
- Criar boundaries por domínio: produtos, usuários, pedidos; courses, checkout, payments; tasks, users, categories.
- Centralizar config sensível e usar variáveis de ambiente.
- Isolar regras repetidas em validators ou services.
- Usar DTOs/serializers seguros para não vazar senha, token, cartão ou segredo.
- Garantir rollback/commit consistente em transações.

## Barra de Qualidade Arquitetural

Use estes critérios para avaliar se o plano MVC está maduro o suficiente antes de implementar:

- **Rastreabilidade**: todo achado aprovado deve estar associado a decisão, etapa, tarefa e validação.
- **Coesão por domínio**: produtos, usuários, pedidos, checkout, payments, tasks ou categorias devem ter boundaries claros.
- **Dependências direcionais**: routes/views dependem de controllers; controllers dependem de services; services dependem de repositories/models; repositories conhecem persistência. Camadas inferiores não devem importar HTTP.
- **Composition root claro**: inicialização de app, banco, middlewares e rotas deve ficar em um ponto previsível.
- **Contratos preservados**: métodos, paths, payloads essenciais, status codes e comandos de boot devem ser preservados salvo decisão aprovada.
- **Segurança por padrão**: segredos, senhas, tokens, cartões e erros internos não devem aparecer em respostas, logs ou DTOs públicos.
- **Validade operacional**: cada etapa deve deixar o projeto em estado executável ou declarar checkpoint/risco.

## Definition of Done MVC

- Entry point claro e pequeno.
- Rotas/views sem SQL direto e sem regra de negócio pesada.
- Controllers coordenam services e respostas.
- Models/repositories isolam dados.
- Configuração sensível fora do código.
- Error handler central cobre erros comuns.
- Endpoints originais continuam respondendo.
- Achados CRITICAL/HIGH tratados ou documentados com justificativa.
- Todos os achados `FIX` ou `PARTIAL` possuem validação registrada.
