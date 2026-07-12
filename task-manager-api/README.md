# task-manager-api

API REST para gerenciamento de tarefas, usuários e categorias, desenvolvida em Python com Flask, Flask-SQLAlchemy e SQLite. O projeto separa rotas, controladores, serviços, repositórios, modelos e schemas de validação e serialização.

## Requisitos

- Python 3.9 ou superior;
- `pip` disponível no ambiente;
- terminal com acesso ao diretório do projeto.

O banco padrão é SQLite e não requer um servidor separado.

## Instalação

Execute a partir do diretório `task-manager-api`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

No Windows PowerShell, ative o ambiente virtual com:

```powershell
.venv\Scripts\Activate.ps1
```

Se o executável do ambiente for `python` em vez de `python3`, substitua-o nos comandos deste documento.

## Configuração

A aplicação lê as seguintes variáveis de ambiente:

| Variável | Padrão | Finalidade |
|---|---|---|
| `DATABASE_URL` | `sqlite:///tasks.db` | URI do SQLAlchemy. Com o padrão do Flask-SQLAlchemy, o arquivo é criado em `instance/tasks.db`. |
| `SECRET_KEY` | Valor aleatório por processo | Assina os tokens de autenticação. Deve ser forte, secreta e estável em ambientes persistentes. |
| `AUTH_TOKEN_MAX_AGE` | `3600` | Validade do token em segundos. Valor não inteiro volta ao padrão. |
| `FLASK_DEBUG` | `false` | Habilita depuração com `1`, `true`, `yes` ou `on`. Não deve ser usado em produção. |
| `HOST` | `0.0.0.0` | Interface em que o servidor de desenvolvimento escuta. |
| `PORT` | `5000` | Porta HTTP. Valor não inteiro volta ao padrão. |
| `SMTP_HOST` | `smtp.gmail.com` | Host utilizado pelo serviço opcional de notificações. |
| `SMTP_PORT` | `587` | Porta SMTP com STARTTLS. |
| `SMTP_USER` | Não definido | Usuário e remetente SMTP. |
| `SMTP_PASSWORD` | Não definido | Senha SMTP. |

Exemplo para desenvolvimento:

```bash
export SECRET_KEY='substitua-por-um-segredo-forte-e-estavel'
export DATABASE_URL='sqlite:///tasks.db'
export AUTH_TOKEN_MAX_AGE=3600
```

Os endpoints atuais não acionam o serviço de notificações. Sem credenciais SMTP, uma chamada direta a esse serviço é ignorada com um aviso no log.

## Banco de dados

As tabelas são criadas automaticamente com `db.create_all()` ao construir a aplicação. Isso permite a primeira execução sem migração manual, mas não substitui um sistema de migrações para futuras alterações de schema.

Com a configuração padrão, o banco persistente está em:

```text
instance/tasks.db
```

Para usar outro SQLite, informe uma URI, por exemplo `sqlite:////caminho/absoluto/tasks.db`. Outros bancos exigem o driver Python correspondente, que não está incluído em `requirements.txt`.

## Dados de demonstração

O seed é opcional. A API funciona sem ele, porém começa com listas vazias. Para carregar os dados de demonstração:

```bash
python3 seed.py
```

> Atenção: cada execução de `seed.py` apaga todas as tarefas, usuários e categorias existentes no banco configurado antes de recriar os exemplos.

O seed cria três usuários:

| Papel | E-mail | Senha | Uso |
|---|---|---|---|
| `admin` | `joao@email.com` | `1234` | Administração completa. |
| `user` | `maria@email.com` | `abcd` | Operações autenticadas comuns. |
| `manager` | `pedro@email.com` | `pass` | Listagem de usuários e relatórios. |

Também são criadas quatro categorias (`Backend`, `Frontend`, `DevOps` e `Bug`) e dez tarefas. Essas credenciais são exclusivamente demonstrativas e devem ser substituídas fora do ambiente local.

## Execução

Com as dependências instaladas e, opcionalmente, o seed carregado:

```bash
python3 app.py
```

A API fica disponível em `http://localhost:5000` com a configuração padrão. Verifique a execução com:

```bash
curl http://localhost:5000/health
```

`GET /health` retorna HTTP `200`, estado `ok` e timestamp UTC. `GET /` retorna o nome e a versão da API.

## Autenticação e papéis

A autenticação usa tokens temporários assinados com `itsdangerous`; não se trata de JWT. Obtenha um token por meio de `POST /login`:

```bash
curl -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"joao@email.com","password":"1234"}'
```

Resposta resumida:

```json
{
  "message": "Login realizado com sucesso",
  "user": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@email.com",
    "role": "admin",
    "active": true
  },
  "token": "TOKEN_ASSINADO"
}
```

Envie o token nas rotas protegidas:

```http
Authorization: Bearer TOKEN_ASSINADO
```

Os tokens expiram após `AUTH_TOKEN_MAX_AGE` segundos e são invalidados após uma reinicialização quando `SECRET_KEY` não é configurada, pois um novo segredo aleatório é gerado. Usuários inativos não conseguem autenticar nem reutilizar tokens existentes.

Papéis disponíveis:

- `user`: acesso aos próprios dados e às operações autenticadas de tarefas;
- `manager`: acesso aos próprios dados, listagem de usuários, dados de outros usuários e relatórios;
- `admin`: inclui administração de usuários e categorias, além dos relatórios.

## Endpoints

### Sistema e tarefas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/` | Público | Nome e versão da API. |
| `GET` | `/health` | Público | Estado e timestamp da aplicação. |
| `GET` | `/tasks` | Público | Lista tarefas com usuário, categoria e indicador de atraso. |
| `GET` | `/tasks/<task_id>` | Público | Consulta uma tarefa. |
| `GET` | `/tasks/search` | Público | Pesquisa tarefas por filtros opcionais. |
| `GET` | `/tasks/stats` | Público | Estatísticas agregadas por status e atraso. |
| `POST` | `/tasks` | Autenticado | Cria uma tarefa. |
| `PUT` | `/tasks/<task_id>` | Autenticado | Atualiza parcialmente uma tarefa. |
| `DELETE` | `/tasks/<task_id>` | Autenticado | Exclui uma tarefa. |

A implementação atual permite que qualquer usuário autenticado crie, altere ou exclua tarefas, independentemente do responsável indicado em `user_id`.

### Usuários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/login` | Público | Valida credenciais e emite token temporário. |
| `POST` | `/users` | Público para papel `user`; `admin` autenticado para papéis privilegiados | Cria um usuário. |
| `GET` | `/users` | `admin` ou `manager` | Lista usuários e quantidade de tarefas. |
| `GET` | `/users/<user_id>` | Próprio usuário, `admin` ou `manager` | Consulta usuário e suas tarefas. |
| `PUT` | `/users/<user_id>` | Próprio usuário ou `admin` | Atualiza parcialmente um usuário. Somente `admin` altera `role` e `active`. |
| `DELETE` | `/users/<user_id>` | `admin` | Exclui usuário e suas tarefas. |
| `GET` | `/users/<user_id>/tasks` | Próprio usuário, `admin` ou `manager` | Lista tarefas do usuário. |

### Categorias e relatórios

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/categories` | Público | Lista categorias e quantidade de tarefas. |
| `POST` | `/categories` | `admin` | Cria uma categoria. |
| `PUT` | `/categories/<category_id>` | `admin` | Atualiza parcialmente uma categoria. |
| `DELETE` | `/categories/<category_id>` | `admin` | Exclui uma categoria. |
| `GET` | `/reports/summary` | `admin` ou `manager` | Visão geral, atrasos, atividade recente e produtividade. |
| `GET` | `/reports/user/<user_id>` | Próprio usuário, `admin` ou `manager` | Estatísticas de um usuário. |

## Contratos JSON

Envie `Content-Type: application/json` nas operações com corpo.

### Tarefa

Exemplo de criação:

```json
{
  "title": "Documentar a API",
  "description": "Revisar contratos e exemplos",
  "status": "pending",
  "priority": 2,
  "user_id": 1,
  "category_id": 1,
  "due_date": "2026-07-31",
  "tags": ["docs", "api"]
}
```

Regras:

- `title` é o único campo obrigatório, com 3 a 200 caracteres;
- `description` assume string vazia;
- `status` aceita `pending`, `in_progress`, `done` ou `cancelled` e assume `pending`;
- `priority` aceita inteiros de `1` (crítica) a `5` (mínima) e assume `3`;
- `user_id` e `category_id` são opcionais, mas devem referenciar registros existentes quando informados;
- `due_date` aceita `YYYY-MM-DD` ou `null`;
- `tags` aceita uma lista de strings, uma string separada por vírgulas ou `null`.

`PUT /tasks/<task_id>` recebe apenas os campos que devem mudar.

Filtros opcionais de `GET /tasks/search`:

- `q`: trecho no título ou na descrição, sem distinção entre maiúsculas e minúsculas;
- `status`: correspondência exata;
- `priority`: inteiro;
- `user_id`: inteiro.

### Usuário

```json
{
  "name": "Ana Souza",
  "email": "ana@example.com",
  "password": "senha-forte",
  "role": "user"
}
```

`name`, `email` e `password` são obrigatórios na criação; a senha deve ter pelo menos 4 caracteres. `role` aceita `user`, `manager` ou `admin` e assume `user`. Uma requisição pública não pode criar papéis privilegiados. O campo opcional `active` deve ser booleano e, em atualizações, somente administradores podem alterá-lo.

Senhas são armazenadas com o hash seguro do Werkzeug e nunca são serializadas. Hashes MD5 legados ainda podem ser validados uma vez e são substituídos automaticamente por um hash atual após login bem-sucedido.

### Categoria

```json
{
  "name": "Documentação",
  "description": "Tarefas de documentação técnica",
  "color": "#3366FF"
}
```

`name` é obrigatório. `description` assume string vazia e `color` deve usar o formato hexadecimal `#RRGGBB`, com padrão `#000000`. Atualizações são parciais.

## Respostas e erros

Respostas de consulta retornam diretamente um objeto ou uma lista JSON, sem envelope. Criações retornam HTTP `201`; consultas, alterações e exclusões bem-sucedidas retornam `200`.

Erros são JSON no formato:

```json
{
  "error": "Descrição do erro"
}
```

Principais códigos: `400` para entrada inválida, `401` para autenticação ausente, inválida ou expirada, `403` para falta de permissão ou usuário inativo no login, `404` para recurso inexistente, `409` para e-mail duplicado e `500` para falha interna sanitizada.

## CORS

O CORS é habilitado globalmente com a configuração padrão do Flask-CORS, sem restrição explícita de origem. Para exposição externa, restrinja as origens permitidas na criação da aplicação ou em um proxy confiável.

## Estrutura do projeto

```text
app.py                 # factory da aplicação e servidor de desenvolvimento
config.py              # configuração por variáveis de ambiente
database.py            # instância do Flask-SQLAlchemy
seed.py                # carga destrutiva de dados de demonstração
controllers/           # adaptação entre HTTP e serviços
middlewares/           # autenticação Bearer e tratamento de erros
models/                # entidades SQLAlchemy
repositories/          # consultas e persistência
routes/                # Blueprints e contratos de rotas
schemas/               # validação, constantes e serialização
services/              # regras de negócio e autorização
utils/                 # funções auxiliares e horário UTC
tests/                 # regressão funcional, segurança e arquitetura
requirements.txt       # dependências Python fixadas
instance/tasks.db      # banco SQLite padrão criado em runtime
```

## Testes

Com as dependências instaladas, execute a partir da raiz do projeto:

```bash
python3 -m unittest discover -v
```

Os testes utilizam SQLite em memória, recriam o schema a cada caso e validam os 22 contratos HTTP, autenticação, autorização, serialização segura, validações e limites arquiteturais. Eles não precisam dos dados de `seed.py`.

## Observações de segurança e produção

- Não versionar `SECRET_KEY`, credenciais SMTP ou tokens reais.
- Utilizar HTTPS para proteger credenciais e tokens em trânsito.
- Trocar imediatamente as senhas demonstrativas se o seed for usado fora de um ambiente local descartável.
- Restringir CORS antes de expor a API publicamente.
- O servidor embutido do Flask e a criação automática de tabelas são adequados para desenvolvimento; em produção, use um servidor WSGI e migrações versionadas.
- Definir regras adicionais de propriedade caso usuários comuns não devam alterar tarefas de terceiros.
