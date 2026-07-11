# Plano de Refatoracao MVC - code-smells-project

## Entradas

- Relatorio de auditoria: `reports/audit-code-smells-project.md`
- Arquivo de estado: `reports/.refactor-arch/STATE.md`
- Aprovado em: 2026-07-10 22:48:07 -0300, resposta afirmativa `s` do usuario

## Arquitetura Alvo

O ponto de entrada `app.py` permanecera compativel e delegara a criacao do Flask para uma application factory no pacote `loja`. Views organizadas em Blueprints extraem HTTP e chamam controllers. Controllers escolhem respostas e coordenam services. Services concentram validacao e casos de uso. Repositories executam exclusivamente SQL parametrizado. Models/DTOs representam dados e impedem vazamento de campos internos. Configuracao, ciclo de vida do SQLite e tratamento de erros ficam centralizados.

```text
app.py
loja/
|-- __init__.py
|-- config.py
|-- database.py
|-- errors.py
|-- models.py
|-- controllers/
|-- repositories/
|-- services/
`-- views/
tests/
```

## Mapeamento de Camadas

| Responsabilidade atual | Arquivos atuais | Camada alvo | Arquivos alvo | Justificativa |
|---|---|---|---|---|
| bootstrap, configuracao e rotas | `app.py` | composicao/configuracao | `app.py`, `loja/__init__.py`, `loja/config.py` | ponto de entrada pequeno e configuracao externa |
| conexao, schema e seed | `database.py` | infraestrutura | `loja/database.py` | conexao por contexto Flask, teardown e inicializacao explicita |
| SQL de todos os dominios | `models.py`, `controllers.py`, `app.py` | repositories | `loja/repositories/*.py` | SQL parametrizado e acesso isolado |
| dados e serializacao | `models.py` | models/DTOs | `loja/models.py` | DTO publico separado de credencial persistida |
| regras e transacoes | `controllers.py`, `models.py` | services | `loja/services/*.py` | casos de uso testaveis sem HTTP |
| adaptacao HTTP | `controllers.py` | controllers | `loja/controllers/*.py` | coordenacao fina e respostas consistentes |
| registro de endpoints | `app.py` | views/routes | `loja/views/*.py` | Blueprints por dominio sem SQL |
| erros e autorizacao | repetidos/inexistentes | transversal | `loja/errors.py`, service/controller administrativo | respostas sanitizadas e controle administrativo |

## Matriz de Cobertura dos Achados

| ID do achado | Severidade | Decisao | Etapas do plano | Validacao | Risco residual |
|---|---|---|---|---|---|
| AP-01 | CRITICAL | FIX | P02, P04 | busca/login malicioso e varredura de `execute` | nenhum SQL livre; consultas dinamicas usam placeholders |
| AP-03 | CRITICAL | FIX | P04, P05 | admin sem/com token e query sempre recusada | segredo administrativo deve ser configurado em producao |
| AP-07 | CRITICAL | FIX | P03, P05 | hash no banco e login de seed/cadastro | legado plaintext migra no primeiro login valido |
| AP-02 | CRITICAL | FIX | P01, P04, P05 | varredura e resposta `/health` | segredo aleatorio de desenvolvimento muda entre processos |
| AP-08 | CRITICAL | FIX | P01, P04, P05 | respostas de usuarios sem `senha`/hash | nenhum |
| AP-04 | HIGH | FIX | P02, P03, P04 | limites de importacao e estrutura final | mais arquivos, compensados por coesao de dominio |
| AP-06 | HIGH | FIX | P02, P03 | services sem SQL e repositories sem regra HTTP | SQLite continua sendo persistencia local sincronica |
| AP-05 | HIGH | FIX | P03, P04 | controllers sem regra de estoque/desconto/hash | notificacoes permanecem adaptador local de logging |
| AP-10 | HIGH | FIX | P01, P02 | conexoes distintas por contexto e teardown | limites normais de concorrencia do SQLite |
| AP-09 | MEDIUM | FIX | P02 | listagem de pedidos usa uma consulta com joins | montagem em memoria cresce com o resultado |
| AP-12 | MEDIUM | FIX | P04 | handlers centralizados e erro 500 sanitizado | detalhes permanecem apenas no log do servidor |
| AP-11 | MEDIUM | FIX | P03 | testes de payload/tipo e validadores reutilizados | sem biblioteca externa de schema |
| AP-14 | LOW | FIX | P01, P03 | configuracao/constantes centralizadas | textos de resposta continuam literais por contrato |
| AP-15 | LOW | FIX | P04, P05 | varredura de imports/prints e remocao dos modulos legados | nenhum |

## Decisoes Arquiteturais

| ID | Decisao | Motivo | Consequencia |
|---|---|---|---|
| DA-01 | usar pacote `loja` e manter `app.py` | evita conflito entre modulo e pacote e preserva `python app.py`/`from app import app` | imports internos passam a ser absolutos pelo pacote |
| DA-02 | usar `sqlite3` e Werkzeug existentes | evita dependencia, ORM e lockfile novos | repositories continuam explicitos e sincronicos |
| DA-03 | conexao por `flask.g` | alinha transacao ao contexto e fecha recursos | services/repositories requerem contexto da aplicacao |
| DA-04 | manter 19 caminhos HTTP | preserva contrato de roteamento | `/admin/query` permanece registrado, mas responde 403 |
| DA-05 | proteger reset com `X-Admin-Token` | controle simples para API de desafio | sem `ADMIN_TOKEN` configurado, reset e negado por padrao |
| DA-06 | migrar senha plaintext no login | compatibilidade com bancos existentes | plaintext pode existir ate o primeiro login valido |
| DA-07 | testes com `unittest` e banco temporario | zero dependencia adicional e isolamento | comando local sera `python3 -m unittest discover -v` |

## Etapas de Refatoracao

### P01 - Fundacao, configuracao e models seguros
- Objetivo: criar pacote, configuracao externa, erros de dominio, DTOs e ciclo de vida SQLite.
- Achados cobertos: AP-02, AP-08, AP-10, AP-14.
- Arquivos esperados: `loja/__init__.py`, `loja/config.py`, `loja/database.py`, `loja/errors.py`, `loja/models.py`.
- Restricoes: nao trocar ainda o ponto de entrada; valores padrao devem ser seguros.
- Validacao: compilacao/importacao dos modulos e schema em banco temporario.

### P02 - Repositories por dominio
- Objetivo: mover todo SQL para repositories parametrizados, com consulta agregada de pedidos.
- Achados cobertos: AP-01, AP-04, AP-06, AP-09, AP-10.
- Arquivos esperados: `loja/repositories/*.py`.
- Restricoes: nenhuma dependencia de Flask HTTP ou regra de resposta.
- Validacao: varredura de SQL concatenado e exercicio de CRUD em banco temporario.

### P03 - Services e regras de negocio
- Objetivo: concentrar validacao, hash/login, pedido/estoque/status e relatorio.
- Achados cobertos: AP-05, AP-06, AP-07, AP-11, AP-14.
- Arquivos esperados: `loja/services/*.py`.
- Restricoes: services nao importam request/jsonify; transacoes compostas fazem rollback.
- Validacao: testes unitarios/de integracao dos fluxos de dominio.

### P04 - Controllers, views, seguranca e composicao
- Objetivo: registrar os 19 endpoints em Blueprints, criar controllers finos, handlers de erro e novo bootstrap.
- Achados cobertos: AP-01, AP-02, AP-03, AP-04, AP-05, AP-08, AP-12, AP-15.
- Arquivos esperados: `loja/controllers/*.py`, `loja/views/*.py`, `loja/__init__.py`, `app.py`.
- Restricoes: manter metodos/caminhos e payloads essenciais, com as seis mudancas de seguranca aprovadas.
- Validacao: route map com 19 endpoints e testes de fumaca por Flask test client.

### P05 - Regressao, documentacao e limpeza
- Objetivo: adicionar cobertura dos contratos, documentar configuracao e remover modulos legados sem uso.
- Achados cobertos: AP-02, AP-03, AP-07, AP-08, AP-15 e regressao de todos.
- Arquivos esperados: `tests/`, `README.md`; remocao de `controllers.py`, `database.py`, `models.py`.
- Restricoes: banco de testes sempre temporario.
- Validacao: suite completa e varredura arquitetural.

### P06 - Validacao operacional final
- Objetivo: validar testes, inicializacao real, HTTP, arquitetura e cobertura dos achados.
- Achados cobertos: AP-01 a AP-15.
- Arquivos esperados: `reports/.refactor-arch/validation-report.md`, `STATE.md`.
- Restricoes: iniciar com banco temporario e encerrar o processo ao final.
- Validacao: `unittest`, servidor+HTTP, scans e compilacao.

## Contrato dos Endpoints a Preservar

| Metodo | Caminho | Comportamento esperado | Validacao |
|---|---|---|---|
| GET | `/` | indice da API | status 200 e mapa de recursos |
| GET | `/produtos` | lista produtos | status 200 e `dados` |
| GET | `/produtos/busca` | filtra produtos | status 200, `dados` e `total` |
| GET | `/produtos/<int:id>` | obtem produto | 200/404 |
| POST | `/produtos` | cria produto | 201 com ID |
| PUT | `/produtos/<int:id>` | atualiza produto | 200/404/400 |
| DELETE | `/produtos/<int:id>` | exclui produto | 200/404 |
| GET | `/usuarios` | lista DTOs publicos | 200 sem senha/hash |
| GET | `/usuarios/<int:id>` | obtem DTO publico | 200/404 sem senha/hash |
| POST | `/usuarios` | cadastra com senha | 201 com ID |
| POST | `/login` | autentica senha | 200/401 |
| POST | `/pedidos` | cria pedido e baixa estoque | 201/400 |
| GET | `/pedidos` | lista pedidos completos | 200 |
| GET | `/pedidos/usuario/<int:usuario_id>` | lista por usuario | 200 |
| PUT | `/pedidos/<int:pedido_id>/status` | muda status | 200/400/404 |
| GET | `/relatorios/vendas` | agrega vendas/desconto | 200 |
| GET | `/health` | saude sanitizada | 200 sem segredo/path/debug |
| POST | `/admin/reset-db` | reset autorizado | 200 com token; 403 sem token |
| POST | `/admin/query` | SQL livre desabilitado | 403 |

## Controles de Risco

- Todos os testes usam `tempfile.TemporaryDirectory`; `loja.db` do usuario nao sera tocado.
- O ponto de entrada so muda depois de infraestrutura, repositories e services existirem.
- A remocao dos modulos legados ocorre somente apos a suite importar a nova estrutura.
- Hash legado e migrado apenas depois de comparacao segura bem-sucedida.
- Mudancas de resposta ficam limitadas ao conjunto de seguranca aprovado no relatorio.
