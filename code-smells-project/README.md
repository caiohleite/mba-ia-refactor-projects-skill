# code-smells-project

API de e-commerce em Python/Flask organizada em MVC e camadas de serviço e persistência.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

Em ambientes sem o alias `python`, use `python3 app.py`. A aplicação sobe em `http://localhost:5000`. O banco SQLite é criado automaticamente no primeiro boot, com produtos e usuários de exemplo.

## Configuração

| Variável | Padrão | Finalidade |
|---|---|---|
| `DATABASE_PATH` | `loja.db` | Caminho do banco SQLite |
| `SECRET_KEY` | valor aleatório por processo | Chave de sessão; defina um segredo estável em produção |
| `ADMIN_TOKEN` | desabilitado | Token exigido em `X-Admin-Token` para `/admin/reset-db` |
| `FLASK_DEBUG` | `false` | Habilita debug apenas quando explicitamente configurado |
| `APP_ENV` | `development` | Nome do ambiente retornado pelo health check |

`POST /admin/query` permanece registrado por compatibilidade, mas a execução de SQL arbitrário é sempre recusada.

## Estrutura

```text
app.py                 # ponto de entrada
loja/
|-- controllers/       # coordenação dos casos de uso
|-- repositories/      # acesso SQLite parametrizado
|-- services/          # regras de negócio e transações
|-- views/             # Blueprints e adaptação HTTP
|-- config.py          # configuração por ambiente
|-- database.py        # conexão, schema e seed
|-- errors.py          # tratamento centralizado
`-- models.py          # entidades e DTOs seguros
tests/                 # regressão dos contratos HTTP
```

## Testes

```bash
python3 -m unittest discover -v
```

Os testes usam bancos SQLite temporários e não alteram `loja.db`.
