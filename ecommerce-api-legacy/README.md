# ecommerce-api-legacy

API de um LMS (Learning Management System) desenvolvida em Node.js, Express e SQLite. O projeto oferece um fluxo público de checkout e operações administrativas para relatório financeiro e exclusão de usuários, organizadas em rotas, controladores, serviços e repositórios.

## Requisitos

- Node.js 18 ou superior;
- npm compatível com o arquivo `package-lock.json`;
- terminal com acesso ao diretório do projeto.

O SQLite é instalado como dependência do projeto e não requer um servidor de banco de dados separado. Em plataformas sem binário pré-compilado compatível, a instalação de `sqlite3` pode exigir as ferramentas nativas de compilação do sistema.

## Instalação

Execute a partir do diretório `ecommerce-api-legacy`:

```bash
npm ci
```

O uso de `npm ci` instala exatamente as versões registradas no lockfile. Para atualizar deliberadamente as dependências e o lockfile, utilize `npm install`.

## Configuração

| Variável | Obrigatória | Padrão | Finalidade |
|---|---|---|---|
| `PORT` | Não | `3000` | Porta HTTP; deve ser um inteiro entre `0` e `65535`. O valor `0` é útil em testes para selecionar uma porta livre. |
| `ADMIN_API_KEY` | Para usar rotas administrativas | Não definida | Chave esperada no cabeçalho `x-admin-api-key`. |

Sem `ADMIN_API_KEY`, a aplicação inicia e o checkout continua disponível, mas as rotas administrativas respondem com HTTP `503`. Quando a variável está configurada, chave ausente ou incorreta responde com HTTP `401`.

Defina uma chave forte fora do código antes de iniciar uma instância que exponha operações administrativas:

```bash
export ADMIN_API_KEY='substitua-por-uma-chave-local-segura'
export PORT=3000
```

No Windows PowerShell, o equivalente é:

```powershell
$env:ADMIN_API_KEY = 'substitua-por-uma-chave-local-segura'
$env:PORT = '3000'
```

## Banco de dados e seed

A aplicação utiliza um banco SQLite em memória (`:memory:`). O schema e os dados iniciais são criados automaticamente no boot; portanto:

- não é necessário executar migrações;
- os dados não são persistidos em disco;
- todo checkout ou exclusão realizado durante a execução é perdido ao reiniciar o processo.

Dados carregados a cada inicialização:

| ID | Tipo | Dados principais |
|---|---|---|
| `1` | Usuário | `Leonan`, `leonan@fullcycle.com.br`; a senha aleatória gerada no boot não pode ser utilizada para autenticação. |
| `1` | Curso | `Clean Architecture`, preço `997.00`, ativo. |
| `2` | Curso | `Docker`, preço `497.00`, ativo. |
| `1` | Matrícula/pagamento | Usuário `1` matriculado no curso `1`, pagamento `PAID` de `997.00`. |

## Execução

Inicie a API com:

```bash
npm start
```

Com a configuração padrão, o serviço fica disponível em `http://localhost:3000`. Uma inicialização bem-sucedida registra no terminal `LMS API rodando na porta 3000.`.

O arquivo `api.http` contém requisições prontas para clientes compatíveis com o formato HTTP Client. Ajuste as variáveis `baseUrl` e `adminApiKey` no início do arquivo conforme o ambiente.

## Autenticação administrativa

As rotas administrativas não usam sessão ou login. Envie a chave configurada em todas as requisições protegidas:

```http
x-admin-api-key: substitua-por-uma-chave-local-segura
```

A comparação da chave é feita de forma resistente a ataques de temporização. O checkout permanece público.

## Endpoints

| Método | Rota | Acesso | Resposta de sucesso | Descrição |
|---|---|---|---|---|
| `POST` | `/api/checkout` | Público | `200` JSON | Cria usuário quando necessário, matrícula, pagamento e auditoria em uma única transação. |
| `GET` | `/api/admin/financial-report` | Chave administrativa | `200` JSON | Lista receita e alunos agrupados por curso. |
| `DELETE` | `/api/users/:id` | Chave administrativa | `200` texto | Exclui o usuário e, por cascata, suas matrículas e pagamentos. |

### Checkout

O endpoint preserva nomes de campos abreviados por compatibilidade com o contrato legado:

```bash
curl -X POST http://localhost:3000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{
    "usr": "Guilherme",
    "eml": "gui@example.com",
    "pwd": "uma-senha-forte",
    "c_id": 2,
    "card": "4111222233334444"
  }'
```

| Campo | Tipo | Regras |
|---|---|---|
| `usr` | string | Nome obrigatório; espaços externos são removidos. |
| `eml` | string | E-mail obrigatório em formato válido; espaços externos são removidos. |
| `pwd` | string | Senha não vazia. Novas senhas são armazenadas com hash `scrypt`, salt aleatório e nunca retornadas. |
| `c_id` | inteiro positivo | ID de um curso ativo. Os cursos disponíveis no seed usam os IDs `1` e `2`. |
| `card` | string | De `12` a `19` dígitos; espaços são ignorados. |

O processamento de pagamento é uma simulação local: cartões iniciados por `4` são aprovados; qualquer outro prefixo resulta em `PAYMENT_DENIED`. Nenhuma integração com gateway externo é realizada e o número do cartão não é persistido.

Resposta de sucesso:

```json
{
  "msg": "Sucesso",
  "enrollment_id": 2
}
```

Se já existir um usuário com o e-mail informado, o checkout reutiliza esse cadastro. O fluxo completo ocorre em uma transação: falhas posteriores à abertura da transação desfazem usuário, matrícula, pagamento e auditoria criados naquela operação.

### Relatório financeiro

```bash
curl http://localhost:3000/api/admin/financial-report \
  -H 'x-admin-api-key: substitua-por-uma-chave-local-segura'
```

O resultado inclui todos os cursos, mesmo sem matrículas. A receita soma somente pagamentos com status `PAID`:

```json
[
  {
    "course": "Clean Architecture",
    "revenue": 997,
    "students": [
      {"student": "Leonan", "paid": 997}
    ]
  },
  {
    "course": "Docker",
    "revenue": 0,
    "students": []
  }
]
```

### Exclusão de usuário

```bash
curl -X DELETE http://localhost:3000/api/users/1 \
  -H 'x-admin-api-key: substitua-por-uma-chave-local-segura'
```

O `id` deve ser um inteiro positivo. A resposta de sucesso é o texto `Usuário deletado.`. Por causa das chaves estrangeiras com exclusão em cascata, matrículas e pagamentos relacionados também são removidos. A implementação atual devolve sucesso mesmo quando o ID não existe.

## Erros

Erros de aplicação são retornados como JSON:

```json
{
  "error": "Descrição do erro",
  "code": "CODIGO_DO_ERRO"
}
```

| HTTP | Código | Situação típica |
|---|---|---|
| `400` | `INVALID_CHECKOUT_PAYLOAD` | Corpo ausente ou campos do checkout inválidos. |
| `400` | `PAYMENT_DENIED` | Cartão não iniciado por `4`. |
| `400` | `INVALID_USER_ID` | ID de exclusão inválido. |
| `401` | `UNAUTHORIZED` | Chave administrativa ausente ou incorreta. |
| `404` | `COURSE_NOT_FOUND` | Curso inexistente ou inativo. |
| `503` | `ADMIN_AUTH_NOT_CONFIGURED` | `ADMIN_API_KEY` não configurada. |
| `500` | `INTERNAL_ERROR` | Falha interna não prevista, sem exposição de detalhes sensíveis. |

Rotas inexistentes seguem o tratamento padrão do Express e podem responder em HTML.

## Arquitetura

```text
src/
|-- config/            # leitura e validação da configuração
|-- controllers/       # adaptação entre HTTP e casos de uso
|-- db/                # conexão, schema, seed e suporte a transações
|-- errors/            # erro de aplicação padronizado
|-- middlewares/       # autenticação administrativa e erros
|-- repositories/      # acesso parametrizado ao SQLite
|-- routes/            # declaração das rotas HTTP
|-- services/          # regras e orquestração de domínio
|-- validators/        # validação do contrato de checkout
|-- app.js             # criação e configuração do Express
`-- server.js          # composição, inicialização e servidor HTTP
test/run.js            # regressão funcional, segurança e arquitetura
api.http               # exemplos executáveis de requisições
package.json           # scripts e dependências
package-lock.json      # versões resolvidas das dependências
```

## Testes

Execute:

```bash
npm test
```

A suíte sobe a aplicação em portas efêmeras e bancos em memória, valida checkout aprovado e recusado, curso inexistente, autenticação administrativa, relatório, exclusão em cascata, hash de senha e restrições arquiteturais. O resultado esperado termina com:

```text
PASS: regressão funcional, segurança e arquitetura MVC
```

## Observações de segurança e operação

- Nunca versionar ou registrar `ADMIN_API_KEY` real.
- Expor a API somente por HTTPS quando houver tráfego externo.
- O checkout é uma simulação educacional: não deve processar cartões reais e não atende, por si só, aos requisitos de um ambiente de pagamentos.
- O banco em memória é adequado para demonstração e testes, não para persistência em produção.
- A API não configura CORS; chamadas de navegadores a partir de outra origem exigem configuração adicional na aplicação ou no proxy.
- O processo Node deve ser encerrado normalmente para liberar o banco e a porta HTTP.
