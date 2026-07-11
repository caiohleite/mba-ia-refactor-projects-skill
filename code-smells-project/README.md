# code-smells-project

API de e-commerce em Python/Flask organizada em MVC e camadas de serviço e persistência.

## Como rodar

```bash
pip install -r requirements.txt
flask --app app init-db
python app.py
```

Em ambientes sem o alias `python`, use `python3 app.py`. A aplicação sobe em `http://localhost:5000`. A inicialização do schema é explícita: o servidor não cria tabelas nem carrega dados durante o boot padrão.

Para carregar produtos de demonstração, execute `flask --app app seed-db`. Uma conta administrativa só é criada quando `SEED_ADMIN_EMAIL` e `SEED_ADMIN_PASSWORD` forem fornecidos pelo ambiente:

```bash
export SEED_ADMIN_EMAIL=admin@example.com
export SEED_ADMIN_PASSWORD='use-um-segredo-forte'
flask --app app seed-db
```

O comando `init-db` migra automaticamente o schema legado válido para a versão atual, com unicidade de email e chaves estrangeiras. Duplicidades ou relações inválidas interrompem a migração para evitar perda silenciosa.

## Configuração

| Variável | Padrão | Finalidade |
|---|---|---|
| `DATABASE_PATH` | `loja.db` | Caminho do banco SQLite |
| `SECRET_KEY` | valor aleatório por processo | Chave de sessão; defina um segredo estável em produção |
| `ADMIN_TOKEN` | desabilitado | Token exigido em `X-Admin-Token` para `/admin/reset-db` |
| `FLASK_DEBUG` | `false` | Habilita debug apenas quando explicitamente configurado |
| `APP_ENV` | `development` | Nome do ambiente retornado pelo health check |
| `AUTO_INIT_DATABASE` | `false` | Inicializa schema no app factory; destinado a testes/ambientes controlados |
| `SEED_DATA` | `false` | Carrega seed junto do auto-init; destinado a testes/ambientes controlados |
| `SEED_ADMIN_NAME` | `Administrator` | Nome da conta admin criada pelo seed explícito |
| `SEED_ADMIN_EMAIL` | desabilitado | Email admin; deve ser usado junto de `SEED_ADMIN_PASSWORD` |
| `SEED_ADMIN_PASSWORD` | desabilitado | Senha admin recebida do ambiente e armazenada somente como hash |
| `CORS_ORIGINS` | nenhuma | Allowlist de origens separadas por vírgula |
| `SESSION_COOKIE_SECURE` | `false` | Deve ser `true` quando a aplicação usar HTTPS |

`POST /admin/query` permanece registrado por compatibilidade, mas a execução de SQL arbitrário é sempre recusada.

## Autenticação e autorização

`POST /login` estabelece uma sessão assinada em cookie `HttpOnly`/`SameSite=Lax`. Em produção, configure uma `SECRET_KEY` estável e habilite `SESSION_COOKIE_SECURE=true` sob HTTPS.

- Catálogo, raiz, health, criação de usuário e login são públicos.
- Alterações de produto, listagem geral de usuários/pedidos, status e relatórios exigem papel `admin`.
- Clientes autenticados podem consultar apenas o próprio usuário/pedidos e criar pedidos apenas para si.
- `/admin/reset-db` mantém a proteção independente por `X-Admin-Token`.

Exemplo com `curl`:

```bash
curl -c cookies.txt -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","senha":"use-um-segredo-forte"}'
curl -b cookies.txt http://localhost:5000/usuarios
```

## Estrutura

```text
app.py                 # ponto de entrada
loja/
|-- controllers/       # coordenação dos casos de uso
|-- repositories/      # acesso SQLite parametrizado
|-- services/          # regras de negócio e transações
|-- views/             # Blueprints e adaptação HTTP
|-- middlewares/       # autenticação, papéis e ownership
|-- config.py          # configuração por ambiente
|-- database.py        # conexão, migração e comandos de seed
|-- errors.py          # tratamento centralizado
`-- models.py          # entidades e DTOs seguros
tests/                 # regressão dos contratos HTTP
```

## Testes

```bash
python3 -m unittest discover -v
```

Os testes usam bancos SQLite temporários e não alteram `loja.db`.
