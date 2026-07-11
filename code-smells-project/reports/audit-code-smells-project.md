# Relatório de Auditoria Arquitetural - code-smells-project

**Gerado em**: 2026-07-11  
**Caminho do projeto**: `.`  
**Stack**: Python 3 + Flask 3.1.1 + SQLite  
**Arquivos analisados**: 30 relevantes (35 arquivos Python inspecionados)  
**LOC aproximado**: 1.442 linhas Python, incluindo testes  
**Domínio**: E-commerce  
**Arquitetura atual**: MVC/em camadas já implementado  
**Estado do fluxo de trabalho**: `reports/.refactor-arch/STATE.md`

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 2 |
| HIGH | 1 |
| MEDIUM | 2 |
| LOW | 2 |

Total de achados: 7

A base atual já atende ao objetivo arquitetural MVC: views/blueprints são finos, controllers coordenam os casos de uso, services contêm regras e transações, repositories isolam SQL e models representam dados. Portanto, **não é necessária uma nova reestruturação para MVC**. Os achados críticos restantes são de segurança e os médios/baixos são melhorias localizadas de persistência e domínio.

## Visão Arquitetural

- Ponto de entrada: `app.py` e application factory em `loja/__init__.py`
- Camada de rotas/views: `loja/views/*.py`
- Camada de controllers: `loja/controllers/*.py`
- Camada de serviços/regras: `loja/services/*.py`
- Camada de dados/modelos: `loja/models.py` e `loja/repositories/*.py`
- Pontos de integração/banco de dados: `loja/database.py` e repositories SQLite
- Principal risco arquitetural: a estrutura MVC está adequada, mas não existe uma fronteira geral de autenticação/autorização para dados e operações de negócio.

## Achados

### CRITICAL Credenciais previsíveis de usuários de seed estão fixadas no código

- **ID**: AP-02
- **Arquivo**: `loja/database.py:20-24`, `loja/database.py:91-100`
- **Evidência**: o seed define emails e senhas conhecidas, incluindo o usuário de tipo `admin` com senha previsível; os valores são hasheados antes da persistência, mas continuam visíveis no repositório e são aceitos pelo endpoint de login.
- **Descrição**: hash seguro protege o banco, mas não transforma uma senha publicada no código em segredo. Toda instância inicializada com o seed compartilha as mesmas credenciais conhecidas.
- **Impacto**: qualquer pessoa com acesso ao código ou aos valores padrão pode autenticar-se como os usuários de exemplo; o risco cresce assim que o tipo `admin` for usado para autorização.
- **Recomendação**: não criar contas com senhas fixas no boot; mover dados de demonstração para comando/fixture explícito, gerar senha temporária fora do código ou exigir configuração segura.
- **Padrão de refatoração**: configuração externa + seed explícito
- **Confiança**: Alta

### CRITICAL Operações privilegiadas de negócio não exigem autenticação ou autorização

- **ID**: AP-03
- **Arquivo**: `loja/views/product_routes.py:26-38`, `loja/views/order_routes.py:13-30`, `loja/views/user_routes.py:21-28`, `loja/__init__.py:10-28`
- **Evidência**: criação/alteração/exclusão de produtos, criação/alteração de pedidos e criação de usuários chamam controllers diretamente. Não há guard/middleware de autenticação; `CORS(app)` usa a política padrão global. Apenas `/admin/reset-db` possui verificação própria de token.
- **Descrição**: o endpoint de login valida credenciais, mas não cria sessão/token nem existe um principal autenticado consumido pelas outras rotas.
- **Impacto**: clientes anônimos podem alterar catálogo, excluir produtos e manipular estado de pedidos, comprometendo integridade e disponibilidade dos dados.
- **Recomendação**: criar autenticação central e guards por papel/ownership; proteger operações de catálogo e status; restringir CORS por configuração; manter o guard administrativo fail-closed.
- **Padrão de refatoração**: middleware/guard de autenticação e autorização
- **Confiança**: Alta

### HIGH Dados pessoais e histórico de pedidos são enumeráveis sem autenticação

- **ID**: AP-08
- **Arquivo**: `loja/views/user_routes.py:11-18`, `loja/models.py:70-77`, `loja/views/order_routes.py:18-25`, `loja/models.py:113-121`
- **Evidência**: `/usuarios` e `/usuarios/<id>` retornam nomes e emails; `/pedidos` e `/pedidos/usuario/<id>` retornam pedidos e itens. Nenhuma dessas rotas verifica identidade ou papel.
- **Descrição**: os DTOs corretamente omitem senha/hash, porém emails, IDs e histórico de compras ainda são dados pessoais e comerciais que não deveriam ser enumeráveis anonimamente.
- **Impacto**: exposição de PII e hábitos de compra, além de permitir correlação por IDs sequenciais.
- **Recomendação**: exigir autenticação, limitar listagem geral a papel administrativo e permitir que clientes consultem apenas o próprio perfil/pedidos; considerar paginação e minimização de campos.
- **Padrão de refatoração**: authorization guard + DTO por caso de uso
- **Confiança**: Alta

### MEDIUM Integridade relacional e unicidade dependem somente da aplicação

- **ID**: AP-06A
- **Arquivo**: `loja/database.py:37-58`, `loja/repositories/product_repository.py:38-43`, `loja/repositories/order_repository.py:95-123`
- **Evidência**: `usuarios.email` não possui `UNIQUE`; `pedidos.usuario_id`, `itens_pedido.pedido_id` e `itens_pedido.produto_id` não declaram chaves estrangeiras. Produtos são excluídos fisicamente e a leitura de pedidos tolera produto ausente como `Desconhecido`.
- **Descrição**: validações em service reduzem erros no caminho normal, mas não impedem corrida de criação de email duplicado nem referências órfãs após deleções ou operações externas.
- **Impacto**: inconsistência silenciosa, duplicidade de identidade e histórico de pedidos degradado.
- **Recomendação**: criar migração versionada com `UNIQUE` e FKs adequadas, escolher explicitamente `RESTRICT`, soft delete ou snapshots para produtos usados em pedidos e mapear violações para erros de domínio.
- **Padrão de refatoração**: constraints no schema + política de deleção
- **Confiança**: Alta

### MEDIUM Criação da aplicação executa DDL e seed automaticamente

- **ID**: AP-06B
- **Arquivo**: `loja/__init__.py:30-31`, `loja/database.py:77-102`
- **Evidência**: toda chamada a `create_app` abre o banco, executa o schema, conta registros e insere seeds quando as tabelas estão vazias.
- **Descrição**: bootstrap HTTP, evolução de schema e carga de demonstração compartilham o mesmo ciclo de vida, sem histórico/versionamento de migrações.
- **Impacto**: startup tem efeitos persistentes, seeds podem aparecer em ambientes indevidos e alterações futuras de schema ficam difíceis de aplicar e reverter de forma controlada.
- **Recomendação**: manter apenas o ciclo de conexão na app factory; mover migração e seed para comandos explícitos e idempotentes, com seed condicionado ao ambiente.
- **Padrão de refatoração**: application factory + migration/seed command
- **Confiança**: Alta

### LOW Limiares de desconto são números mágicos

- **ID**: AP-14
- **Arquivo**: `loja/services/report_service.py:24-32`
- **Evidência**: os patamares `10000`, `5000`, `1000` e percentuais `10%`, `5%`, `2%` estão embutidos na função.
- **Descrição**: a regra está na camada correta, mas seus parâmetros não têm nomes de domínio nem configuração explícita.
- **Impacto**: mudanças comerciais exigem editar lógica e aumentam o risco de interpretação incorreta.
- **Recomendação**: extrair faixas para constantes imutáveis nomeadas ou política de desconto injetável e cobrir limites com testes unitários.
- **Padrão de refatoração**: substituir números mágicos por política nomeada
- **Confiança**: Alta

### LOW Campo `ativo` não participa da política de ciclo de vida do produto

- **ID**: AP-15
- **Arquivo**: `loja/database.py:27-36`, `loja/models.py:22-47`, `loja/repositories/product_repository.py:6-15`, `loja/repositories/product_repository.py:38-43`
- **Evidência**: `ativo` é criado, materializado e exposto, mas listagem/consulta não filtram por ele e a exclusão executa `DELETE` físico.
- **Descrição**: o campo sugere soft delete, porém não há comportamento correspondente, deixando uma responsabilidade residual e ambígua.
- **Impacto**: consumidores podem interpretar `ativo` como garantia inexistente e a exclusão física agrava referências órfãs.
- **Recomendação**: decidir e documentar a política: implementar desativação/filtragem ou remover o campo por migração se ele não pertence ao domínio.
- **Padrão de refatoração**: consolidar política de ciclo de vida
- **Confiança**: Alta

## Achados de APIs Obsoletas

Nenhum uso de API obsoleta foi identificado com as evidências disponíveis. A varredura não encontrou os padrões legados aplicáveis do catálogo e a suíte executou em Python 3.13/Flask sem `DeprecationWarning` observado.

## Verificações negativas relevantes

- SQL dinâmico usa apenas fragmentos estruturais controlados; entradas externas seguem como parâmetros vinculados.
- Senhas novas e seeds são persistidos com `werkzeug.security.generate_password_hash`.
- Hashes de senha não são serializados nas respostas públicas.
- Exceções inesperadas são registradas no servidor e retornam mensagem genérica ao cliente.
- O endpoint legado `/admin/query` recusa toda execução de SQL.
- Listagem de pedidos usa joins e agrupamento em memória, sem N+1.

## Alvos de Refatoração MVC

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|
| Estrutura MVC principal | `loja/views`, `controllers`, `services`, `repositories`, `models.py` | manter | responsabilidades já estão separadas adequadamente |
| Autenticação/autorização | apenas token local no fluxo admin | middleware/guards e serviço de identidade | proteger operações e dados sem engrossar routes/controllers |
| Seed de usuários | `loja/database.py` | comando/fixture explícito e configuração externa | remover credenciais fixas do boot |
| Evolução do banco | `loja/database.py` na app factory | migrations/CLI de infraestrutura | separar boot HTTP de DDL/seed |
| Integridade/ciclo do produto | schema + repositories | constraints, política de deleção e service | impedir órfãos e resolver o campo `ativo` |
| Política de desconto | `ReportService` | constantes/policy de domínio | tornar a regra explícita e testável |

## Necessidade de Fase 3

- **Reestruturação para MVC**: não necessária; o projeto já está em MVC/em camadas.
- **Correções localizadas**: recomendadas, com prioridade para AP-02, AP-03 e AP-08.
- **Recomendação ao decidir a confirmação**: responda `n` se o objetivo for estritamente migrar para MVC; responda `s` somente se deseja autorizar uma Fase 3 de hardening localizado, mantendo a arquitetura atual e os contratos HTTP tanto quanto possível.

## Plano de Validação para a Fase 3

- Comando de inicialização: `PYTHONDONTWRITEBYTECODE=1 python3 app.py`
- Endpoints de testes de fumaça: os 19 contratos registrados em `STATE.md`, com foco em `GET /health`, `GET /produtos`, `POST /login`, operações protegidas e endpoints admin
- Comando de testes: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`
- Preparação de dados: banco SQLite temporário criado por `tests/test_api.py`
- Arquivo de estado: `reports/.refactor-arch/STATE.md`

## Pré-condições da Fase 3

- O humano revisou este relatório.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints foi registrado em `STATE.md`.
- A refatoração deve avançar tarefa por tarefa usando `refactor-plan.md` e `refactor-tasks.md`.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
