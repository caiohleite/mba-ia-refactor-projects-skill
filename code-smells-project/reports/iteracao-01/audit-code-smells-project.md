# Relatório de Auditoria Arquitetural - code-smells-project

**Gerado em**: 2026-07-10 22:39:25 -0300  
**Caminho do projeto**: `.`  
**Stack**: Python 3 + Flask 3.1.1 + SQLite  
**Arquivos analisados**: 4  
**LOC aproximado**: 780  
**Domínio**: API de e-commerce/loja  
**Arquitetura atual**: monólito procedural em camadas, com MVC parcial e responsabilidades misturadas  
**Estado do fluxo de trabalho**: `reports/.refactor-arch/STATE.md`

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 5 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 2 |

Total de achados: 14

## Visão Arquitetural

- Ponto de entrada: `app.py`
- Camada de rotas: regras registradas em `app.py`; não há Blueprints nem módulo de routes/views
- Camada de dados/modelos: `models.py` e `database.py`
- Locais com lógica de negócio: `controllers.py` e `models.py`
- Pontos de integração/banco de dados: `database.py`, `models.py`, `controllers.py` e `app.py`
- Principal risco arquitetural: qualquer requisição pode alcançar SQL ou operações destrutivas sem uma fronteira de autorização, enquanto regras, persistência e representação HTTP permanecem acopladas.

## Achados

### CRITICAL Execução e injeção de SQL por entrada externa

- **ID**: AP-01
- **Arquivo**: `app.py:59-78`; `models.py:43-68`; `models.py:105-169`; `models.py:275-300`
- **Evidência**: `/admin/query` envia o campo `sql` do JSON diretamente a `cursor.execute`; vários métodos de dados também concatenam nomes, credenciais, filtros e itens recebidos pelas rotas em comandos SQL.
- **Descrição**: a aplicação não estabelece uma fronteira de consultas permitidas nem usa parâmetros vinculados de forma consistente. O endpoint administrativo amplia o problema de injeção para execução remota de SQL arbitrário.
- **Impacto**: leitura, alteração ou exclusão integral do banco; bypass do login; corrupção de estoque e pedidos.
- **Recomendação**: desabilitar a execução arbitrária, parametrizar todas as consultas e encapsular o acesso em repositories por domínio.
- **Padrão de refatoração**: Trocar SQL Concatenado por Parâmetros; Dividir Objeto Deus por Domínio
- **Confiança**: Alta

### CRITICAL Endpoints administrativos destrutivos sem proteção

- **ID**: AP-03
- **Arquivo**: `app.py:47-78`
- **Evidência**: os endpoints públicos `/admin/reset-db` e `/admin/query` não verificam identidade, papel ou credencial; o primeiro apaga as quatro tabelas e o segundo executa comandos fornecidos pelo cliente.
- **Descrição**: operações administrativas críticas estão registradas no mesmo aplicativo e expostas sem autenticação/autorização.
- **Impacto**: perda completa de dados, acesso indevido e indisponibilidade da aplicação por uma única requisição.
- **Recomendação**: manter as rotas somente se houver necessidade explícita, protegê-las por autenticação/autorização administrativa e auditoria, e recusar SQL livre.
- **Padrão de refatoração**: Afinar Rotas e Controllers; Centralizar Tratamento de Erros
- **Confiança**: Alta

### CRITICAL Senhas armazenadas e comparadas em texto puro

- **ID**: AP-07
- **Arquivo**: `database.py:27-34`; `database.py:75-82`; `models.py:105-130`
- **Evidência**: a coluna `senha` recebe credenciais de seed e cadastro sem hash; o login compara a senha diretamente no SQL.
- **Descrição**: não há derivação de chave, salt ou função de verificação de senha.
- **Impacto**: qualquer leitura do banco revela credenciais reutilizáveis; o comprometimento se estende a outros serviços onde usuários repetirem senhas.
- **Recomendação**: gerar hashes com `werkzeug.security`, verificar via função dedicada e definir migração compatível para registros existentes.
- **Padrão de refatoração**: Substituir Criptografia Fraca; Criar DTO Seguro
- **Confiança**: Alta

### CRITICAL Segredo e modo debug fixados e expostos

- **ID**: AP-02
- **Arquivo**: `app.py:6-9`; `app.py:80-88`; `controllers.py:276-290`
- **Evidência**: `SECRET_KEY` e `DEBUG` são constantes no código, o servidor inicia com `debug=True`, e `/health` devolve a chave secreta, o caminho do banco e o estado de debug.
- **Descrição**: configuração sensível e operacional está misturada ao bootstrap e à representação HTTP.
- **Impacto**: vazamento de segredo de assinatura de sessão, exposição de detalhes internos e risco de execução/debug inadequado fora do desenvolvimento.
- **Recomendação**: centralizar configuração por ambiente, exigir segredo externo e retornar somente indicadores não sensíveis no health check.
- **Padrão de refatoração**: Extrair Configuração e Segredos; Criar DTO Seguro
- **Confiança**: Alta

### CRITICAL Vazamento de senhas pelos endpoints de usuários

- **ID**: AP-08
- **Arquivo**: `models.py:72-103`; `controllers.py:128-144`
- **Evidência**: as funções de listagem e busca incluem `senha` nos dicionários devolvidos diretamente por `GET /usuarios` e `GET /usuarios/<id>`; ambas as rotas são públicas.
- **Descrição**: o modelo de persistência é reutilizado como DTO público, sem lista explícita de campos permitidos.
- **Impacto**: extração não autenticada de todas as credenciais em texto puro.
- **Recomendação**: criar DTOs/serializadores públicos que nunca incluam senha ou hash e proteger os recursos de usuário conforme o papel.
- **Padrão de refatoração**: Criar DTO Seguro; Afinar Rotas e Controllers
- **Confiança**: Alta

### HIGH Arquivo de dados concentra múltiplos domínios e responsabilidades

- **ID**: AP-04
- **Arquivo**: `models.py:1-314`
- **Evidência**: um único módulo implementa CRUD de produtos e usuários, autenticação, pedidos, estoque, relatório de vendas, serialização e SQL.
- **Descrição**: `models.py` é um arquivo Deus procedural; mudanças em qualquer agregado atravessam a mesma dependência e conexão.
- **Impacto**: alto acoplamento, baixa coesão, testes difíceis e maior risco de regressão durante evolução do domínio.
- **Recomendação**: separar models/DTOs, repositories e services por produto, usuário/autenticação, pedido e relatório.
- **Padrão de refatoração**: Dividir Objeto Deus por Domínio; Afinar Rotas e Controllers
- **Confiança**: Alta

### HIGH Persistência, transação e regra de negócio misturadas

- **ID**: AP-06
- **Arquivo**: `models.py:133-169`; `models.py:235-283`; `controllers.py:264-292`; `app.py:47-78`
- **Evidência**: criação do pedido valida estoque, calcula total, grava pedido/itens e reduz estoque na mesma função SQL; relatório calcula desconto dentro do módulo de dados; controller e ponto de entrada também abrem cursores.
- **Descrição**: não existe repository ou unidade de trabalho; as fronteiras HTTP, domínio e persistência acessam a conexão diretamente.
- **Impacto**: regras não podem ser testadas isoladamente e falhas intermediárias podem deixar uma transação pendente na conexão global.
- **Recomendação**: repositories devem executar SQL parametrizado, enquanto services coordenam regras e transações explícitas.
- **Padrão de refatoração**: Trocar SQL Concatenado por Parâmetros; Dividir Objeto Deus por Domínio
- **Confiança**: Alta

### HIGH Regras e efeitos de negócio dentro dos controllers

- **ID**: AP-05
- **Arquivo**: `controllers.py:24-62`; `controllers.py:188-220`; `controllers.py:237-255`
- **Evidência**: controllers validam categoria/preço/estoque, simulam três notificações e decidem efeitos por status; no cancelamento, a mensagem afirma devolução de estoque, mas a persistência apenas altera o status.
- **Descrição**: casos de uso e efeitos externos estão acoplados ao ciclo HTTP e divididos entre controller e model.
- **Impacto**: inconsistência de regras, dificuldade de reuso e um comportamento de cancelamento que não executa o efeito anunciado.
- **Recomendação**: extrair services de produto e pedido, portas de notificação e política explícita de transição/restauração de estoque.
- **Padrão de refatoração**: Afinar Rotas e Controllers; Dividir Objeto Deus por Domínio; Extrair Validação Reutilizável
- **Confiança**: Alta

### HIGH Conexão SQLite global e compartilhada entre requisições

- **ID**: AP-10
- **Arquivo**: `database.py:4-11`; `database.py:86`
- **Evidência**: `db_connection` é global, criada com `check_same_thread=False`, reutilizada indefinidamente e nunca fechada por contexto da aplicação.
- **Descrição**: o ciclo de vida da conexão não acompanha o ciclo de vida da requisição e não há isolamento de transações concorrentes.
- **Impacto**: vazamento de estado transacional, concorrência frágil, bloqueios e dificuldade de substituir o banco em testes.
- **Recomendação**: usar conexão por contexto Flask com `g`, teardown explícito e injeção da dependência nos repositories.
- **Padrão de refatoração**: Extrair Configuração e Segredos; Dividir Objeto Deus por Domínio
- **Confiança**: Alta

### MEDIUM Consultas N+1 na montagem de pedidos

- **ID**: AP-09
- **Arquivo**: `models.py:171-233`
- **Evidência**: para cada pedido há uma consulta de itens e, para cada item, outra consulta de nome do produto; a duplicação existe nas listagens global e por usuário.
- **Descrição**: o número de consultas cresce com pedidos e itens, em vez de usar uma consulta em lote/join.
- **Impacto**: latência e carga de banco crescentes, além de código de montagem duplicado.
- **Recomendação**: carregar pedidos, itens e produtos com join ou lotes e agrupar o resultado em memória uma única vez.
- **Padrão de refatoração**: Remover N+1 Consultas
- **Confiança**: Alta

### MEDIUM Tratamento de erros duplicado e vazamento de exceções

- **ID**: AP-12
- **Arquivo**: `controllers.py:5-292`; `app.py:68-78`
- **Evidência**: quase todos os handlers repetem `except Exception` e devolvem `str(e)` com status 500; não há rollback, classificação de erros nem handler central.
- **Descrição**: erros de validação, domínio e infraestrutura não possuem tipos ou mapeamento consistente.
- **Impacto**: detalhes de SQL podem vazar, erros esperados viram 500 e transações falhas podem permanecer abertas.
- **Recomendação**: criar exceções de domínio, rollback na fronteira transacional, handler Flask central e respostas públicas sanitizadas.
- **Padrão de refatoração**: Centralizar Tratamento de Erros
- **Confiança**: Alta

### MEDIUM Validação manual, duplicada e incompleta

- **ID**: AP-11
- **Arquivo**: `controllers.py:24-96`; `controllers.py:146-201`; `controllers.py:237-243`
- **Evidência**: criação e atualização de produto repetem verificações; categorias e status são listas locais; login/pedido assumem que o JSON é objeto e não validam tipos, quantidades positivas ou existência do usuário.
- **Descrição**: regras de entrada e regras de domínio estão dispersas em handlers e não formam schemas reutilizáveis.
- **Impacto**: respostas inconsistentes, exceções por payload malformado e caminhos para estoque/total inválidos.
- **Recomendação**: extrair schemas/validators e constantes do domínio, mantendo mensagens e status HTTP compatíveis onde não houver correção de segurança.
- **Padrão de refatoração**: Extrair Validação Reutilizável
- **Confiança**: Alta

### LOW Valores operacionais e enumerações mágicas

- **ID**: AP-14
- **Arquivo**: `app.py:7-8`; `app.py:88`; `controllers.py:52-54`; `controllers.py:242-250`; `database.py:5`
- **Evidência**: segredo, debug, porta, caminho do banco, categorias e estados válidos são literais espalhados.
- **Descrição**: políticas configuráveis e vocabulário de domínio não possuem fonte única.
- **Impacto**: alterações exigem busca textual e podem divergir entre camadas.
- **Recomendação**: mover operação para configuração e domínio para constantes/enums coesos.
- **Padrão de refatoração**: Extrair Configuração e Segredos; Extrair Validação Reutilizável
- **Confiança**: Alta

### LOW Importações mortas e logging por print

- **ID**: AP-15
- **Arquivo**: `database.py:2`; `models.py:2`; `controllers.py:5-255`
- **Evidência**: `os` e `sqlite3` são importados sem uso nos respectivos módulos; controllers registram sucesso, falha, e-mail e notificações com `print`.
- **Descrição**: resíduos de implementação e saída não estruturada atravessam os handlers.
- **Impacto**: ruído, baixa observabilidade e dificuldade de controlar dados de log por ambiente.
- **Recomendação**: remover imports mortos e usar logging estruturado/sanitizado na preocupação transversal apropriada.
- **Padrão de refatoração**: Centralizar Tratamento de Erros
- **Confiança**: Alta

## Achados de APIs Obsoletas

Nenhum uso de API obsoleta foi identificado com as evidências disponíveis. As APIs Flask, Flask-Cors e `sqlite3` utilizadas não apresentam, no código analisado, um candidato documentado como legado que justifique um achado AP-13.

| API | Localização | Uso atual | Equivalente moderno | Confiança |
|---|---|---|---|---|
| Nenhuma identificada | N/A | N/A | N/A | Alta |

## Alvos de Refatoração MVC

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|
| Raiz de composição/configuração | `app.py`, `database.py` | `app/__init__.py`, `app/config.py`, `run.py` | separar factory, configuração e execução |
| Views/routes | `app.py`, `controllers.py` | `app/routes/` com Blueprints | manter adaptação HTTP fina e preservar caminhos |
| Controllers | `controllers.py` | `app/controllers/` por domínio | coordenar casos de uso sem SQL/regra pesada |
| Services | `controllers.py`, `models.py` | `app/services/` | concentrar autenticação, pedido, estoque, relatório e notificações |
| Models/DTOs | dicionários em `models.py` | `app/models/` e `app/serializers/` | representar domínio sem expor campos internos |
| Repositories | SQL em quatro módulos | `app/repositories/` | parametrizar consultas e isolar SQLite |
| Banco/migração | `database.py` | `app/database.py`, inicialização explícita | controlar conexão, transação, schema e seed |
| Middlewares/transversais | inexistente | `app/errors.py`, autenticação/autorização e logging | centralizar segurança e erros |
| Testes | inexistente | `tests/` | congelar contratos e casos críticos antes/depois da mudança |

## Mudanças Observáveis Propostas

A aprovação da Fase 3 autoriza planejar e implementar estas mudanças específicas de segurança, sem remover os caminhos HTTP existentes:

- `GET /usuarios` e `GET /usuarios/<id>` deixarão de retornar o campo `senha`.
- `GET /health` deixará de retornar `secret_key`, `db_path` e `debug`.
- `POST /admin/query` não aceitará SQL arbitrário; a rota será mantida, mas recusará a operação ou será limitada a uma operação segura documentada no plano.
- `POST /admin/reset-db` exigirá autorização administrativa configurável.
- Erros 500 deixarão de devolver texto interno de exceções.
- Credenciais persistidas passarão a usar hash; o payload de cadastro e login continuará aceitando `senha`.

Os demais métodos, caminhos, códigos de sucesso e formatos públicos devem ser preservados, salvo incompatibilidade documentada no plano e aprovada antes da tarefa correspondente.

## Plano de Validação para a Fase 3

- Comando de inicialização documentado: `python app.py` (o ambiente atual não possui o alias `python`)
- Comando de inicialização disponível localmente: `python3 app.py`
- Baseline já verificada: importação do Flask e registro dos 19 endpoints com `PYTHONDONTWRITEBYTECODE=1 python3 -c ...`
- Endpoints de testes de fumaça: todos os 19 contratos registrados em `STATE.md`, com foco em `GET /`, `GET /health`, CRUD de produtos, usuários/login, pedidos/estoque/relatório e controles administrativos
- Comando de testes: não encontrado; não existem testes no projeto
- Preparação de dados: usar banco SQLite temporário e seed controlado para não alterar `loja.db`
- Arquivo de estado: `reports/.refactor-arch/STATE.md`

## Pré-condições da Fase 3

- O humano revisou este relatório e as mudanças observáveis de segurança.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints foi registrado em `STATE.md`.
- A refatoração deve avançar tarefa por tarefa usando `refactor-plan.md` e `refactor-tasks.md`.
- Cada um dos 14 achados deve receber decisão e tarefa ou justificativa explícita antes da implementação.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
