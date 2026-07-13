# code-smells-project

API REST de e-commerce desenvolvida em Python com Flask e SQLite. A aplicação segue uma organização inspirada em MVC, com separação entre rotas, controladores, serviços, repositórios e modelos.

## Requisitos

- Python 3.9 ou superior;
- `pip` disponível no ambiente;
- terminal com acesso ao diretório do projeto.

O SQLite é utilizado pela biblioteca padrão do Python e não requer um servidor de banco de dados separado.

## Instalação

Execute os comandos a partir do diretório `code-smells-project`:

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

A configuração é feita por variáveis de ambiente. Nenhuma variável é obrigatória para uma execução local básica.

| Variável | Padrão | Finalidade |
|---|---|---|
| `DATABASE_PATH` | `loja.db` | Caminho do arquivo SQLite, relativo ao diretório de execução quando não for absoluto. |
| `SECRET_KEY` | Valor aleatório por processo | Assina a sessão. Defina um segredo estável e forte fora do código em ambientes persistentes. |
| `ADMIN_TOKEN` | Não definido | Habilita e protege `POST /admin/reset-db` por meio do cabeçalho `X-Admin-Token`. |
| `FLASK_DEBUG` | `false` | Habilita o modo de depuração com `1`, `true`, `yes` ou `on`. Não deve ser habilitado em produção. |
| `APP_ENV` | `development` | Identificador de ambiente exibido por `GET /health`. |
| `AUTO_INIT_DATABASE` | `false` | Inicializa ou migra o schema ao criar a aplicação. Indicado apenas para testes ou ambientes controlados. |
| `SEED_DATA` | `false` | Executa o seed quando `AUTO_INIT_DATABASE` também estiver habilitado. |
| `SEED_ADMIN_NAME` | `Administrator` | Nome da conta administrativa criada pelo seed. |
| `SEED_ADMIN_EMAIL` | Não definido | E-mail da conta administrativa do seed; deve ser usado com `SEED_ADMIN_PASSWORD`. |
| `SEED_ADMIN_PASSWORD` | Não definido | Senha da conta administrativa do seed; é persistida somente como hash. |
| `CORS_ORIGINS` | Nenhuma origem | Lista de origens permitidas, separadas por vírgula. Credenciais CORS são habilitadas apenas para essa lista. |
| `SESSION_COOKIE_SECURE` | `false` | Envia o cookie de sessão somente por HTTPS quando habilitado. |

Exemplo de configuração para desenvolvimento:

```bash
export SECRET_KEY='substitua-por-um-segredo-forte'
export APP_ENV='development'
export CORS_ORIGINS='http://localhost:3000,http://127.0.0.1:3000'
```

## Banco de dados e dados iniciais

Crie ou atualize o schema antes da primeira execução:

```bash
flask --app app init-db
```

O servidor não cria tabelas nem carrega dados durante a inicialização padrão. O comando `init-db` também migra automaticamente um schema legado compatível para a versão atual, adicionando unicidade de e-mail e chaves estrangeiras. Duplicidades ou relações inválidas interrompem a migração para evitar perda silenciosa de dados.

Para inserir os dez produtos de demonstração:

```bash
flask --app app seed-db
```

Para criar também uma conta administrativa, forneça e-mail e senha em conjunto antes do seed:

```bash
export SEED_ADMIN_NAME='Administrador'
export SEED_ADMIN_EMAIL='admin@example.com'
export SEED_ADMIN_PASSWORD='use-um-segredo-forte'
flask --app app seed-db
```

O seed não duplica produtos quando a tabela já contém registros nem recria um administrador cujo e-mail já esteja cadastrado.

## Execução

Com o ambiente virtual ativo e o banco inicializado:

```bash
python3 app.py
```

A API fica disponível em `http://localhost:5000` e escuta em todas as interfaces de rede (`0.0.0.0`). Confirme a execução com:

```bash
curl http://localhost:5000/health
```

Uma resposta bem-sucedida usa HTTP `200` e informa o estado da aplicação, a versão, o ambiente e as contagens das tabelas.

## Autenticação e autorização

`POST /login` cria uma sessão assinada e devolve um cookie `HttpOnly` com `SameSite=Lax`. Clientes HTTP devem preservar e reenviar esse cookie nas rotas protegidas. Em produção, configure uma `SECRET_KEY` estável e `SESSION_COOKIE_SECURE=true` sob HTTPS.

Papéis disponíveis:

- `admin`: acesso a usuários, todos os pedidos, manutenção do catálogo, alteração de status e relatórios;
- `cliente`: consulta o próprio usuário e os próprios pedidos e cria pedidos somente para si.

Catálogo, página raiz, health check, cadastro de usuário e login são públicos. Não existe uma rota de logout; o cliente deve descartar o cookie para encerrar a sessão localmente.

Exemplo de login e uso do cookie:

```bash
curl -c cookies.txt -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","senha":"use-um-segredo-forte"}'

curl -b cookies.txt http://localhost:5000/usuarios
```

## Endpoints

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/` | Público | Metadados e links principais da API. |
| `GET` | `/health` | Público | Estado da aplicação e contagens do banco. |
| `GET` | `/produtos` | Público | Lista produtos ativos. |
| `GET` | `/produtos/busca` | Público | Pesquisa produtos ativos por filtros. |
| `GET` | `/produtos/<id>` | Público | Consulta um produto ativo. |
| `POST` | `/produtos` | `admin` | Cria um produto. |
| `PUT` | `/produtos/<id>` | `admin` | Substitui os dados editáveis de um produto. |
| `DELETE` | `/produtos/<id>` | `admin` | Desativa um produto sem apagar seu histórico. |
| `POST` | `/usuarios` | Público | Cadastra um cliente. |
| `POST` | `/login` | Público | Autentica e cria uma sessão. |
| `GET` | `/usuarios` | `admin` | Lista todos os usuários sem expor senhas. |
| `GET` | `/usuarios/<id>` | Próprio usuário ou `admin` | Consulta um usuário. |
| `POST` | `/pedidos` | Sessão autenticada | Cria um pedido para o próprio cliente; administradores podem criar para qualquer usuário. |
| `GET` | `/pedidos` | `admin` | Lista todos os pedidos. |
| `GET` | `/pedidos/usuario/<usuario_id>` | Próprio usuário ou `admin` | Lista os pedidos de um usuário. |
| `PUT` | `/pedidos/<pedido_id>/status` | `admin` | Altera o status de um pedido. |
| `GET` | `/relatorios/vendas` | `admin` | Retorna o resumo de vendas. |
| `POST` | `/admin/reset-db` | Token administrativo | Remove todos os dados; exige `X-Admin-Token`. |
| `POST` | `/admin/query` | Sempre recusado | Rota mantida por compatibilidade; SQL arbitrário permanece desabilitado. |

### Filtros de produtos

`GET /produtos/busca` aceita os parâmetros opcionais:

- `q`: trecho pesquisado no nome ou na descrição;
- `categoria`: categoria exata;
- `preco_min`: preço mínimo;
- `preco_max`: preço máximo.

As categorias aceitas na criação e atualização são `informatica`, `moveis`, `vestuario`, `geral`, `eletronicos` e `livros`.

### Corpos JSON

Cadastro de usuário:

```json
{
  "nome": "Maria Silva",
  "email": "maria@example.com",
  "senha": "uma-senha-forte"
}
```

Criação ou atualização completa de produto. `descricao` e `categoria` são opcionais e assumem `""` e `"geral"`, respectivamente:

```json
{
  "nome": "Teclado Mecânico",
  "descricao": "Teclado ABNT2",
  "preco": 299.9,
  "estoque": 15,
  "categoria": "informatica"
}
```

Criação de pedido:

```json
{
  "usuario_id": 2,
  "itens": [
    {"produto_id": 1, "quantidade": 2}
  ]
}
```

Os itens repetidos são consolidados. A criação reduz o estoque de forma transacional; o cancelamento o repõe. O corpo para mudança de status é:

```json
{
  "status": "aprovado"
}
```

Os status válidos são `pendente`, `aprovado`, `enviado`, `entregue` e `cancelado`.

## Respostas e erros

As respostas de negócio são JSON e normalmente incluem `sucesso` e, quando aplicável, `dados` ou `mensagem`. Erros seguem o formato:

```json
{
  "erro": "Descrição do erro",
  "sucesso": false
}
```

Principais códigos HTTP: `200` para sucesso, `201` para criação, `400` para entrada inválida, `401` para ausência ou falha de autenticação, `403` para falta de permissão, `404` para recurso inexistente, `409` para e-mail duplicado e `500` para falha interna sanitizada.

## Estrutura do projeto

```text
app.py                 # ponto de entrada e servidor de desenvolvimento
loja/
|-- controllers/       # coordenação dos casos de uso
|-- repositories/      # acesso parametrizado ao SQLite
|-- services/          # regras de negócio e transações
|-- views/             # Blueprints e adaptação HTTP
|-- middlewares/       # autenticação, papéis e controle de propriedade
|-- config.py          # configuração por ambiente
|-- database.py        # conexão, schema, migração e comandos CLI
|-- errors.py          # tratamento centralizado de erros
`-- models.py          # entidades e contratos de serialização
tests/                 # testes de regressão dos contratos HTTP
requirements.txt       # dependências Python fixadas
```

## Testes

Com as dependências instaladas, execute a partir da raiz do projeto:

```bash
python3 -m unittest discover -v
```

Os testes criam bancos SQLite temporários, exercitam autenticação, autorização, CRUD, pedidos, migração e tratamento de erros e não alteram o arquivo `loja.db`.

## Observações de segurança

- Não versionar `SECRET_KEY`, `ADMIN_TOKEN` ou credenciais reais.
- Executar a aplicação atrás de HTTPS em produção e habilitar `SESSION_COOKIE_SECURE`.
- Restringir `CORS_ORIGINS` às origens realmente autorizadas.
- Manter `POST /admin/reset-db` desabilitado quando não for necessário; a operação é destrutiva e independente da sessão de usuário.
- O servidor embutido do Flask é destinado a desenvolvimento, não a produção.
