# ecommerce-api

LMS API com fluxo de checkout em Node.js, Express e SQLite, organizada em camadas MVC.

## Como rodar

```bash
npm install
ADMIN_API_KEY="uma-chave-local-segura" npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

| Variável | Obrigatória | Padrão | Finalidade |
|---|---|---|---|
| `PORT` | não | `3000` | porta HTTP |
| `ADMIN_API_KEY` | para rotas administrativas | nenhum | valor esperado no header `x-admin-api-key` |

Sem `ADMIN_API_KEY`, a aplicação inicia normalmente, mas as operações administrativas respondem `503`. Chave ausente ou incorreta responde `401` quando a variável está configurada.

## Endpoints

- `POST /api/checkout`: checkout público.
- `GET /api/admin/financial-report`: relatório protegido.
- `DELETE /api/users/:id`: exclusão protegida, incluindo dados dependentes.

## Arquitetura

- `routes/`: declaração das rotas HTTP.
- `controllers/`: adaptação entre HTTP e casos de uso.
- `services/`: regras e orquestração de domínio.
- `repositories/`: acesso parametrizado ao SQLite.
- `db/`: conexão, schema, seed e transações.
- `middlewares/`: autenticação administrativa e erros.
- `server.js`: raiz de composição e inicialização.
