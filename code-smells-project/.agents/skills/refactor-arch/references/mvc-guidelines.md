# Guidelines De Arquitetura MVC

Use estas regras na Fase 3 para definir a arquitetura alvo. O objetivo nao e impor uma estrutura identica para todas as tecnologias, mas preservar o mesmo contrato de responsabilidades.

## Responsabilidades

| Camada | Responsabilidade | Nao deve conter |
|---|---|---|
| Config | Ler ambiente, defaults seguros, flags e conexoes externas | Segredos hardcoded, regras de negocio |
| Models | Entidades, schemas, mapeamento ORM, invariantes simples | HTTP request/response, queries de relatorio complexas, logs externos |
| Repositories/Data Access | Consultas, comandos de persistencia e transacoes simples | Regras de checkout, notificacoes, serializacao HTTP |
| Services/Use Cases | Regras de negocio, orquestracao de dominio, transacoes compostas | Detalhes de Flask/Express, formato de resposta HTTP |
| Controllers | Coordenar caso de uso, converter erros de dominio em status, escolher DTO | SQL direto, regra de negocio pesada, chamadas externas soltas |
| Views/Routes | Definir rotas, extrair input HTTP, chamar controller, devolver resposta | Calculo de dominio, acesso direto a banco, validacao longa duplicada |
| Middlewares | Erros, auth, logging, CORS, request context | Regras de dominio |
| App/Composition Root | Criar app, registrar rotas, configurar dependencias e iniciar servidor | Handlers de negocio ou queries |

## Estrutura Recomendada Para Flask

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

Variacoes aceitaveis:

- usar `routes/` no lugar de `views/` quando o framework ou projeto ja usa esse nome;
- manter `database.py` se ele for apenas extension/composition de banco;
- usar blueprints por dominio.

## Estrutura Recomendada Para Express

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

Variacoes aceitaveis:

- manter CommonJS se o projeto ja usa `require`;
- separar `app.js` (configura express) de `server.js` (listen);
- encapsular SQLite callbacks em repositories antes de converter para Promises, se a mudanca menor reduzir risco.

## Principios De Refatoracao

- Preservar contrato externo primeiro; melhorar internals depois.
- Preferir pequenas movidas com imports ajustados a reescritas amplas.
- Manter nomes de dominio em portugues/ingles conforme o projeto ja usa.
- Criar boundaries por dominio: produtos, usuarios, pedidos; courses, checkout, payments; tasks, users, categories.
- Centralizar config sensivel e usar variaveis de ambiente.
- Isolar regras repetidas em validators ou services.
- Usar DTOs/serializers seguros para nao vazar senha, token, cartao ou segredo.
- Garantir rollback/commit consistente em transacoes.

## Barra De Qualidade Arquitetural

Use estes criterios para avaliar se o plano MVC esta maduro o suficiente antes de implementar:

- **Rastreabilidade**: todo finding aprovado deve estar associado a decisao, etapa, tarefa e validacao.
- **Coesao por dominio**: produtos, usuarios, pedidos, checkout, payments, tasks ou categorias devem ter boundaries claros.
- **Dependencias direcionais**: routes/views dependem de controllers; controllers dependem de services; services dependem de repositories/models; repositories conhecem persistencia. Camadas inferiores nao devem importar HTTP.
- **Composition root claro**: inicializacao de app, banco, middlewares e rotas deve ficar em um ponto previsivel.
- **Contratos preservados**: metodos, paths, payloads essenciais, status codes e comandos de boot devem ser preservados salvo decisao aprovada.
- **Seguranca por padrao**: segredos, senhas, tokens, cartoes e erros internos nao devem aparecer em respostas, logs ou DTOs publicos.
- **Validade operacional**: cada etapa deve deixar o projeto em estado executavel ou declarar checkpoint/risco.

## Definition Of Done MVC

- Entry point claro e pequeno.
- Rotas/views sem SQL direto e sem regra de negocio pesada.
- Controllers coordenam services e respostas.
- Models/repositories isolam dados.
- Configuracao sensivel fora do codigo.
- Error handler central cobre erros comuns.
- Endpoints originais continuam respondendo.
- Findings CRITICAL/HIGH tratados ou documentados com justificativa.
- Todos os findings `FIX` ou `PARTIAL` possuem validacao registrada.
