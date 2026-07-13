# Relatório de Auditoria Arquitetural - task-manager-api

**Gerado em**: 2026-07-12  
**Caminho do projeto**: `task-manager-api/`  
**Stack**: Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 + SQLAlchemy 2.0.51 + SQLite  
**Arquivos analisados**: 15  
**LOC aproximado**: 1.158  
**Domínio**: gerenciamento de tarefas, usuários, categorias e relatórios  
**Arquitetura atual**: MVC parcial; Blueprints acumulam View/Route, Controller, Service e Repository  
**Estado do fluxo de trabalho**: `reports/.refactor-arch/STATE.md`

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 4 |
| HIGH | 3 |
| MEDIUM | 4 |
| LOW | 2 |

Total de achados: 13

## Visão Arquitetural

- Ponto de entrada: `app.py`.
- Camada de rotas: `routes/task_routes.py`, `routes/user_routes.py` e `routes/report_routes.py`.
- Camada de dados/modelos: `database.py` e `models/*.py`.
- Locais com lógica de negócio: principalmente os três arquivos de rotas; parte menor em `models/task.py`, `models/user.py` e `services/notification_service.py`.
- Pontos de integração/banco de dados: SQLAlchemy/SQLite em todas as rotas; SMTP em `services/notification_service.py`.
- Principal risco arquitetural: endpoints sem autenticação executam operações privilegiadas enquanto regras, acesso a dados e respostas estão fortemente acoplados às rotas.

## Achados

### CRITICAL Segredos fixados no código

- **ID**: AP-02
- **Arquivo**: `app.py:11-13`; `services/notification_service.py:7-10`
- **Evidência**: a chave secreta Flask e credenciais SMTP são literais versionados no código.
- **Descrição**: configuração sensível está acoplada à implementação e não usa o `python-dotenv` já declarado.
- **Impacto**: qualquer leitor do repositório obtém credenciais; a chave Flask comprometida invalida garantias de assinatura de sessão e as credenciais SMTP podem ser abusadas.
- **Recomendação**: centralizar configuração e carregar segredos de variáveis de ambiente, sem padrões reais ou sensíveis.
- **Padrão de refatoração**: 1. Extrair Configuração e Segredos.
- **Confiança**: Alta

### CRITICAL Endpoints privilegiados e escalonamento de papel sem proteção

- **ID**: AP-03
- **Arquivo**: `routes/user_routes.py:42-78`; `routes/user_routes.py:92-151`; `routes/task_routes.py:225-238`; `routes/report_routes.py:12-101`; `routes/report_routes.py:211-223`
- **Evidência**: qualquer cliente pode criar/alterar um usuário com papel `admin`, excluir usuários/tarefas/categorias e consultar relatórios, sem middleware de autenticação ou autorização.
- **Descrição**: o login não protege nenhuma rota, e o parâmetro `role` fornecido pelo próprio cliente é aceito nos fluxos de criação e atualização.
- **Impacto**: permite escalonamento de privilégio, destruição de dados e acesso não autorizado a dados operacionais.
- **Recomendação**: implementar autenticação real, autorização por papel e proteção explícita das operações de leitura sensível e mutação.
- **Padrão de refatoração**: 3. Afinar Rotas e Controllers; 8. Centralizar Tratamento de Erros.
- **Confiança**: Alta

### CRITICAL Hash de senha fraco e token de autenticação previsível

- **ID**: AP-07
- **Arquivo**: `models/user.py:27-32`; `routes/user_routes.py:185-211`
- **Evidência**: senhas são armazenadas com MD5 sem salt; o login devolve `fake-jwt-token-<id>` sem assinatura, expiração ou validação posterior.
- **Descrição**: MD5 não é adequado para senhas e o valor chamado de token é derivável a partir do ID público do usuário.
- **Impacto**: hashes obtidos podem ser quebrados rapidamente, e o token não fornece autenticação confiável.
- **Recomendação**: usar `werkzeug.security` com salt/custo e emitir/verificar credenciais de sessão ou tokens assinados com expiração.
- **Padrão de refatoração**: 6. Substituir Criptografia Fraca; 7. Criar DTO Seguro.
- **Confiança**: Alta

### CRITICAL Hash de senha exposto nas respostas HTTP

- **ID**: AP-08
- **Arquivo**: `models/user.py:16-25`; `routes/user_routes.py:27-40`; `routes/user_routes.py:80-86`; `routes/user_routes.py:127-129`; `routes/user_routes.py:207-210`
- **Evidência**: `User.to_dict()` inclui `password`, e essa representação é devolvida em consulta, criação, atualização e login.
- **Descrição**: o mesmo DTO interno é usado como representação pública, expondo o hash de senha.
- **Impacto**: amplia drasticamente o dano de qualquer acesso ao endpoint e facilita ataques offline contra hashes MD5.
- **Recomendação**: criar serialização pública que nunca contenha senha/hash e usar DTOs específicos para resposta.
- **Padrão de refatoração**: 7. Criar DTO Seguro.
- **Confiança**: Alta

### HIGH Arquivos de rota atuam como objetos Deus

- **ID**: AP-04
- **Arquivo**: `routes/task_routes.py:1-299`; `routes/user_routes.py:1-211`; `routes/report_routes.py:1-223`
- **Evidência**: arquivos de 211 a 299 linhas registram HTTP, validam entrada, consultam o ORM, controlam transações, calculam regras e serializam respostas.
- **Descrição**: os nomes de pastas sugerem camadas, mas não há controllers, repositories ou schemas em código-fonte; as rotas executam todas essas funções.
- **Impacto**: baixa testabilidade, alto acoplamento ao Flask/SQLAlchemy e grande raio de impacto para mudanças.
- **Recomendação**: dividir por domínio e responsabilidade, deixando Blueprints apenas com roteamento e adaptação HTTP.
- **Padrão de refatoração**: 3. Afinar Rotas e Controllers; 4. Dividir Objeto Deus por Domínio.
- **Confiança**: Alta

### HIGH Regras de negócio e relatórios pesados nas rotas

- **ID**: AP-05
- **Arquivo**: `routes/task_routes.py:11-59`; `routes/task_routes.py:273-297`; `routes/user_routes.py:153-183`; `routes/report_routes.py:12-101`; `routes/report_routes.py:103-155`
- **Evidência**: cálculo de atraso, taxa de conclusão, estatísticas por prioridade/estado e produtividade por usuário acontece dentro dos handlers HTTP.
- **Descrição**: regras de domínio estão duplicadas e presas ao contexto de requisição do Flask.
- **Impacto**: impede testes unitários isolados, favorece divergência de regras e torna relatórios difíceis de otimizar.
- **Recomendação**: mover casos de uso e cálculos para services de tarefas e relatórios; controllers apenas coordenam entrada e saída.
- **Padrão de refatoração**: 3. Afinar Rotas e Controllers; 4. Dividir Objeto Deus por Domínio; 9. Extrair Validação Reutilizável.
- **Confiança**: Alta

### HIGH Persistência e transações controladas diretamente pelas rotas

- **ID**: AP-06
- **Arquivo**: `routes/task_routes.py:1-5`; `routes/task_routes.py:116-154`; `routes/task_routes.py:217-238`; `routes/user_routes.py:1-4`; `routes/user_routes.py:67-90`; `routes/user_routes.py:127-151`; `routes/report_routes.py:1-5`; `routes/report_routes.py:157-223`
- **Evidência**: os Blueprints importam `db`, executam queries e fazem `add/delete/commit/rollback` diretamente.
- **Descrição**: transporte HTTP e persistência não possuem fronteira; a exclusão em cascata de tarefas do usuário também é implementada manualmente na rota.
- **Impacto**: acoplamento forte, transações inconsistentes e dificuldade de substituir ou simular a persistência.
- **Recomendação**: criar repositories por entidade e services para coordenar regras e unidade transacional.
- **Padrão de refatoração**: 4. Dividir Objeto Deus por Domínio.
- **Confiança**: Alta

### MEDIUM Consultas N+1 em listagens e relatórios

- **ID**: AP-09
- **Arquivo**: `routes/task_routes.py:14-59`; `routes/report_routes.py:53-68`; `routes/report_routes.py:157-165`
- **Evidência**: a listagem consulta usuário e categoria dentro do loop de tarefas; relatórios consultam tarefas por usuário e contagem por categoria dentro de loops.
- **Descrição**: o número de queries cresce linearmente com o volume retornado.
- **Impacto**: latência e carga de banco aumentam rapidamente conforme tarefas, usuários e categorias crescem.
- **Recomendação**: usar eager loading para relacionamentos e agregações/joins para contagens.
- **Padrão de refatoração**: 5. Remover N+1 Consultas.
- **Confiança**: Alta

### MEDIUM Validação, serialização e regras duplicadas

- **ID**: AP-11
- **Arquivo**: `routes/task_routes.py:16-59`; `routes/task_routes.py:89-145`; `routes/task_routes.py:162-215`; `routes/user_routes.py:49-78`; `routes/user_routes.py:102-125`; `routes/user_routes.py:159-181`; `utils/helpers.py:57-116`
- **Evidência**: regras de título/status/prioridade/tags, cálculo de atraso e construção de DTOs aparecem em múltiplos handlers; há helpers equivalentes que não são usados pelas rotas.
- **Descrição**: não existe schema único para entrada ou saída, apesar de Marshmallow constar nas dependências.
- **Impacto**: endpoints aceitam formatos diferentes e correções precisam ser repetidas em vários locais.
- **Recomendação**: centralizar constantes e validações em schemas/validators e consolidar serializers/DTOs.
- **Padrão de refatoração**: 9. Extrair Validação Reutilizável; 7. Criar DTO Seguro.
- **Confiança**: Alta

### MEDIUM Tratamento de erros inconsistente e exceções ocultadas

- **ID**: AP-12
- **Arquivo**: `routes/task_routes.py:61-63`; `routes/task_routes.py:134-154`; `routes/task_routes.py:200-238`; `routes/user_routes.py:80-90`; `routes/user_routes.py:127-151`; `routes/report_routes.py:182-223`; `utils/helpers.py:43-50`
- **Evidência**: existem vários `except:` nus e capturas genéricas; erros são reduzidos a mensagens diferentes e logs via `print`, sem tratador central.
- **Descrição**: falhas de programação e infraestrutura são tratadas como erros esperados, perdendo contexto e padronização.
- **Impacto**: defeitos ficam ocultos, respostas variam por endpoint e a observabilidade é insuficiente.
- **Recomendação**: definir exceções de domínio e handlers Flask centrais, mantendo rollback nos limites transacionais.
- **Padrão de refatoração**: 8. Centralizar Tratamento de Erros.
- **Confiança**: Alta

### MEDIUM Uso da API legada `Query.get()`

- **ID**: AP-13
- **Arquivo**: `routes/task_routes.py:42-51`; `routes/task_routes.py:67-67`; `routes/task_routes.py:117-122`; `routes/task_routes.py:158-158`; `routes/task_routes.py:188-195`; `routes/task_routes.py:227-227`; `routes/user_routes.py:29-29`; `routes/user_routes.py:94-94`; `routes/user_routes.py:136-136`; `routes/user_routes.py:155-155`; `routes/report_routes.py:105-105`; `routes/report_routes.py:192-192`; `routes/report_routes.py:213-213`
- **Evidência**: a aplicação usa `Model.query.get()` repetidamente com SQLAlchemy 2.0.51, versão confirmada no ambiente local.
- **Descrição**: `Query.get()` pertence à interface legada; a API de sessão é o caminho moderno no SQLAlchemy 2.x.
- **Impacto**: acumula dívida de compatibilidade e avisos, dificultando futuras atualizações.
- **Recomendação**: substituir isoladamente por `db.session.get(Model, id)` e validar todos os endpoints afetados.
- **Padrão de refatoração**: 10. Modernizar APIs Obsoletas.
- **Confiança**: Alta

### LOW Nomes obscuros e valores mágicos espalhados

- **ID**: AP-14
- **Arquivo**: `routes/task_routes.py:16-16`; `routes/report_routes.py:24-28`; `routes/report_routes.py:33-68`; `models/task.py:38-48`; `utils/helpers.py:110-116`
- **Evidência**: variáveis como `t`, `u`, `p1` a `p5` e listas/faixas de estado/prioridade aparecem como literais; constantes já definidas em `utils/helpers.py` não são consumidas.
- **Descrição**: a linguagem de domínio e as restrições não têm fonte única.
- **Impacto**: reduz legibilidade e facilita inconsistências ao alterar regras.
- **Recomendação**: adotar nomes de domínio e constantes/enums compartilhados junto dos schemas.
- **Padrão de refatoração**: 9. Extrair Validação Reutilizável.
- **Confiança**: Alta

### LOW Importações mortas e responsabilidades residuais

- **ID**: AP-15
- **Arquivo**: `app.py:7-7`; `models/task.py:3-3`; `routes/task_routes.py:7-7`; `routes/user_routes.py:6-6`; `routes/report_routes.py:7-8`; `utils/helpers.py:1-7`; `services/notification_service.py:1-48`
- **Evidência**: há diversos imports sem uso; `format_date`/`calculate_percentage` são importados mas não chamados; o serviço de notificação não é integrado ao fluxo; Marshmallow, Requests e python-dotenv estão declarados sem uso atual.
- **Descrição**: resíduos sugerem camadas planejadas, mas não efetivamente conectadas.
- **Impacto**: aumenta ruído, dependências e falsa percepção de separação arquitetural.
- **Recomendação**: remover resíduos após a extração das camadas e integrar apenas componentes com responsabilidade definida.
- **Padrão de refatoração**: 8. Centralizar Tratamento de Erros; 9. Extrair Validação Reutilizável.
- **Confiança**: Alta

## Achados de APIs Obsoletas

| API | Localização | Uso atual | Equivalente moderno | Confiança |
|---|---|---|---|---|
| `Model.query.get(id)` / `Query.get()` | rotas de tarefas, usuários e relatórios listadas no AP-13 | busca por chave primária | `db.session.get(Model, id)` | Alta |
| `datetime.utcnow()` com datetime ingênuo | `app.py:24`; `models/*.py`; `routes/*.py`; `seed.py:66-74`; `services/notification_service.py:35`; `utils/helpers.py:38` | timestamps e comparação de prazos sem timezone | `datetime.now(timezone.utc)` com estratégia consistente de armazenamento | Média |

## Alvos de Refatoração MVC

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|
| Configuração e criação da aplicação | `app.py` | `config.py` + application factory/composition root | retirar segredos e efeitos colaterais de importação |
| Rotas HTTP | `routes/*.py` | Blueprints finos em `routes/` | manter contrato e delegar coordenação |
| Coordenação HTTP/casos de uso | handlers em `routes/*.py` | `controllers/task_controller.py`, `user_controller.py`, `category_controller.py`, `report_controller.py` | separar Flask das regras |
| Regras de domínio | handlers e models | `services/task_service.py`, `user_service.py`, `auth_service.py`, `category_service.py`, `report_service.py` | centralizar casos de uso e transações |
| Persistência | queries nas rotas | `repositories/*_repository.py` | encapsular ORM, agregações e eager loading |
| Validação e DTOs | rotas, `to_dict`, helpers | `schemas/` e serializers públicos | eliminar duplicação e vazamento de senha |
| Autenticação/autorização e erros | ausente/disperso | `middlewares/auth.py`, `middlewares/error_handler.py` | proteger endpoints e padronizar falhas |
| Modelos | `models/*.py` | manter modelos enxutos | representar dados e invariantes sem HTTP |

## Plano de Validação para a Fase 3

- Comando de inicialização: `venv/bin/python app.py`.
- Endpoints de testes de fumaça: `GET /`, `GET /health`, `GET /tasks`, `GET /tasks/1`, `GET /tasks/search?q=login`, `GET /tasks/stats`, `GET /users`, `GET /users/1`, `GET /users/1/tasks`, `POST /login`, `GET /reports/summary`, `GET /reports/user/1`, `GET /categories`; operações POST/PUT/DELETE serão exercitadas sobre banco temporário ou dados controlados.
- Comando de testes: não encontrado; será necessário criar testes de contrato/regressão ou executar smoke tests via cliente Flask.
- Preparação de dados: `venv/bin/python seed.py` recria os dados; deve ser executado somente em banco local/temporário de validação.
- Verificação estática já executada: parse AST dos 15 arquivos, sem erro.
- Arquivo de estado: `reports/.refactor-arch/STATE.md`.

## Pré-condições da Fase 3

- O humano revisou este relatório.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints foi registrado em `STATE.md`.
- A refatoração deve avançar tarefa por tarefa usando `refactor-plan.md` e `refactor-tasks.md`.
- Mudanças de segurança que alterem o contrato observável (token, autorização e remoção do campo `password`) devem ser registradas e validadas explicitamente no plano.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
