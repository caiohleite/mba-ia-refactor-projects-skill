# Relatório de Auditoria Arquitetural - task-manager-api (iteração 02)

**Gerado em**: 2026-07-12 11:45:34 -03  
**Caminho do projeto**: `.`  
**Stack**: Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1/SQLAlchemy 2.0.51  
**Arquivos analisados**: 44  
**LOC aproximado**: 1.941  
**Domínio**: gerenciamento de tarefas, usuários, categorias e relatórios  
**Arquitetura atual**: MVC/em camadas adequado  
**Estado do fluxo de trabalho**: `reports/iteracao-02/.refactor-arch/STATE.md`

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 6 |
| LOW | 1 |

Total de achados: 7.

Não foram encontradas violações graves de MVC, SQL inseguro, segredos fixos, endpoints administrativos desprotegidos, DTOs com senha, N+1 comprovado ou regras de negócio pesadas nas rotas/controllers. A quantidade de achados reflete riscos residuais reais; nenhum CRITICAL/HIGH foi fabricado para repetir o perfil do código legado.

**Conclusão arquitetural**: o projeto já está estruturado em MVC/camadas de forma efetiva. Não é necessária outra reorganização arquitetural para atender ao objetivo MVC. Os achados abaixo pedem hardening e limpeza pontuais; o primeiro também depende da decisão de negócio sobre tarefas serem públicas ou privadas.

## Visão Arquitetural

- Ponto de entrada/composição: `app.py`.
- Camada de rotas/views: `routes/*.py`, fina e sem ORM.
- Camada de controllers: `controllers/*.py`, responsável por HTTP e serialização.
- Camada de negócio: `services/*.py`.
- Camada de dados/modelos: `models/*.py` e `repositories/*.py`.
- Validação/DTOs: `schemas/*.py`.
- Preocupações transversais: `middlewares/*.py` e `config.py`.
- Banco de dados: SQLite por padrão via Flask-SQLAlchemy.
- Principal risco residual: o contrato atual permite leitura anônima de dados de tarefas, sem documentação que confirme que essa exposição é intencional.

## Achados

### MEDIUM Leitura anônima de tarefas e metadados relacionados

- **ID**: AP-08
- **Arquivo**: `routes/task_routes.py:10-17`, `routes/task_routes.py:38-45`, `controllers/task_controller.py:10-20`, `schemas/serializers.py:1-20`, `tests/test_api.py:61-64`
- **Evidência**: quatro endpoints GET de tarefas não usam `authenticated`; a listagem inclui descrição, responsáveis/categorias, datas e tags, e os testes formalizam resposta 200 sem token.
- **Descrição**: mutações estão protegidas, mas listagem, detalhe, busca e estatísticas são públicas. O repositório não documenta se tarefas devem ser informação pública.
- **Impacto**: se o domínio tratar tarefas como dados internos, usuários anônimos podem enumerar conteúdo operacional e vínculos com usuários. Se a publicidade for intencional, o risco pode ser aceito e documentado.
- **Recomendação**: confirmar o contrato de privacidade; se privado, aplicar `authenticated` e autorização por proprietário/papel aos quatro endpoints, atualizando os testes de contrato.
- **Padrão de refatoração**: middleware/guard de autenticação já existente; não requer reorganização MVC.
- **Confiança**: Média, porque a exposição é comprovada, mas a intenção de negócio não está documentada.

### MEDIUM Segredo de assinatura efêmero quando a variável de ambiente não existe

- **ID**: AP-02
- **Arquivo**: `config.py:18-22`
- **Evidência**: `SECRET_KEY` recebe um valor aleatório durante a importação quando `SECRET_KEY` não está no ambiente.
- **Descrição**: o fallback evita segredo fixo, porém muda entre processos/reinícios. Tokens emitidos por uma instância podem falhar após reinício ou em outro worker.
- **Impacto**: invalidação imprevisível de sessões e comportamento inconsistente em execução multiprocesso; não há vazamento de segredo.
- **Recomendação**: exigir `SECRET_KEY` estável fora de testes/desenvolvimento ou persistir explicitamente uma chave de desenvolvimento; falhar cedo em ambiente de produção quando ausente.
- **Padrão de refatoração**: configuração explícita por ambiente.
- **Confiança**: Alta.

### MEDIUM Compatibilidade MD5 ainda aceita hashes fracos

- **ID**: AP-07
- **Arquivo**: `models/user.py:21-31`, `services/auth_service.py:15-26`, `tests/test_api.py:181-204`
- **Evidência**: senhas novas usam Werkzeug, mas qualquer valor hexadecimal de 32 caracteres é tratado como MD5 e só é atualizado após login bem-sucedido.
- **Descrição**: trata-se de uma ponte de migração, não do algoritmo padrão. A inspeção somente leitura do banco local encontrou três usuários e nenhum hash legado, reduzindo o risco imediato nesta cópia.
- **Impacto**: bancos externos que ainda contenham hashes legados permanecem vulneráveis a quebra offline até o primeiro login de cada usuário; a ponte perpetua código criptográfico fraco após a migração local ter terminado.
- **Recomendação**: executar migração/reset explícito para contas legadas, registrar prazo de remoção e então retirar o caminho MD5; se houver bancos externos, inventariá-los antes.
- **Padrão de refatoração**: migração de credenciais com remoção de compatibilidade temporária.
- **Confiança**: Alta para o código; Média para bases externas não disponíveis.

### MEDIUM Política de senha permite apenas quatro caracteres

- **ID**: AP-11
- **Arquivo**: `schemas/constants.py:1-9`, `schemas/validators.py:112-118`, `seed.py:17-35`
- **Evidência**: `MIN_PASSWORD_LENGTH = 4`; o validador aceita esse tamanho e o seed cria contas com senhas curtas conhecidas.
- **Descrição**: a validação está corretamente centralizada, mas a regra é fraca para autenticação real. As credenciais do seed são apropriadas apenas para demonstração local.
- **Impacto**: facilita adivinhação/brute force se a configuração for usada fora de um ambiente descartável.
- **Recomendação**: elevar a política, impedir seed de demonstração em ambientes não locais e documentar claramente as credenciais como não produtivas.
- **Padrão de refatoração**: validação centralizada já existente; alteração pontual de política/configuração.
- **Confiança**: Alta.

### MEDIUM Application factory cria schema e a importação instancia a aplicação

- **ID**: AP-06
- **Arquivo**: `app.py:11-40`, `seed.py:1-10`
- **Evidência**: cada chamada de `create_app()` executa `db.create_all()`; o módulo também chama `create_app()` ao ser importado.
- **Descrição**: a raiz de composição está organizada, mas sua construção tem efeito persistente. Importar `app` pode criar/alterar o arquivo SQLite, e testes criam primeiro a aplicação padrão antes da aplicação in-memory.
- **Impacto**: ciclo de vida do banco implícito, dificuldade para migrações e efeitos colaterais em CLI, testes e workers.
- **Recomendação**: retirar `create_all()` da factory e disponibilizar comando explícito de inicialização/migração; manter uma factory sem efeitos persistentes.
- **Padrão de refatoração**: application factory com lifecycle explícito.
- **Confiança**: Alta.

### MEDIUM Script de seed usa a API `Query` legada

- **ID**: AP-13
- **Arquivo**: `seed.py:12-15`, `seed.py:95-97`
- **Evidência**: o script usa `Task.query.delete()` e `Model.query.count()`. Na instalação local, `sqlalchemy.orm.Query.__doc__` declara `Query` como construção legada desde SQLAlchemy 2.0.
- **Descrição**: a aplicação principal usa corretamente `db.select`/`db.session`, mas o seed mantém o estilo 1.x.
- **Impacto**: inconsistência de APIs e custo futuro quando suporte legado for reduzido; o impacto está limitado ao script de desenvolvimento.
- **Recomendação**: substituir por `db.session.execute(db.delete(Model))` e contagens via `db.select(db.func.count(...))`/`db.session.scalar`.
- **Padrão de refatoração**: modernização da API de persistência.
- **Confiança**: Alta.

### LOW Código residual sem consumidores e documentação desatualizada

- **ID**: AP-15
- **Arquivo**: `utils/helpers.py:1-87`, `services/notification_service.py:1-56`, `services/__init__.py:1-8`, `README.md:1-13`
- **Evidência**: a busca por referências encontra as funções de `utils/helpers.py` e `NotificationService` apenas nas próprias definições; o serviço nem sequer é exportado por `services/__init__.py`. O README ainda descreve a base como parcialmente separada e não documenta autenticação, variáveis de ambiente ou testes.
- **Descrição**: resíduos do legado aumentam a superfície cognitiva e o README não representa a arquitetura atual.
- **Impacto**: confusão de manutenção e risco de futuros consumidores escolherem helpers duplicados ou um serviço de notificações incompleto.
- **Recomendação**: remover o que não fizer parte do produto ou integrar/testar explicitamente; atualizar o README com arquitetura, autenticação, configuração e testes.
- **Padrão de refatoração**: remoção de código morto e sincronização de documentação.
- **Confiança**: Alta.

## Achados de APIs Obsoletas

| API | Localização | Uso atual | Equivalente moderno | Confiança |
|---|---|---|---|---|
| `Model.query.delete()` | `seed.py:12-14` | limpeza de tabelas | `db.session.execute(db.delete(Model))` | Alta |
| `Model.query.count()` | `seed.py:95-97` | contagem após seed | `db.session.scalar(db.select(db.func.count(Model.id)))` | Alta |

Não foram encontrados `Query.get`, `datetime.utcnow`, hooks removidos do Flask ou APIs obsoletas no fluxo HTTP principal.

## Alvos de Refatoração MVC

Nenhum alvo de reorganização MVC é necessário. Caso a Fase 3 seja aprovada, o escopo adequado é hardening/limpeza pontual:

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|
| Política de acesso a tarefas | `routes/task_routes.py`/services | middleware e regras existentes | decidir e aplicar privacidade sem mudar camadas |
| Configuração/autenticação | `config.py`, `models/user.py` | mesmos módulos, com lifecycle explícito | estabilizar chave e encerrar migração MD5 |
| Lifecycle do banco | `app.py`, `seed.py` | comando explícito de inicialização/migração | remover efeitos persistentes da factory |
| Resíduos/documentação | `utils/helpers.py`, `services/notification_service.py`, `README.md` | remover, integrar ou documentar | reduzir superfície morta |

## Plano de Validação para a Fase 3

- Comando de inicialização: `venv/bin/python app.py` (ou `python app.py`).
- Endpoints de fumaça: os 22 métodos/caminhos registrados em `STATE.md`.
- Comando de testes: `venv/bin/python -m unittest -v`.
- Preparação de dados: usar SQLite in-memory nos testes; não executar o seed destrutivo sobre banco do usuário.
- Verificação estática já executada: parse AST dos 44 arquivos, com sucesso.
- Testes não executados nesta fase: importar `app` chama `create_all()` no banco padrão, o que violaria a restrição de não modificar banco antes da confirmação.
- Arquivo de estado: `reports/iteracao-02/.refactor-arch/STATE.md`.

## Pré-condições da Fase 3

- O humano revisou este relatório.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints foi registrado em `STATE.md`.
- Qualquer Fase 3 deve preservar a estrutura MVC existente e tratar apenas achados aprovados.
- A privacidade dos endpoints de tarefas deve ser decidida antes de mudar o contrato HTTP.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]

**Recomendação da auditoria**: `n` para nova refatoração MVC, pois a arquitetura já está adequada. Uma resposta `s` deve ser entendida como autorização para hardening/limpeza pontual dos achados, com decisão explícita sobre a privacidade das tarefas antes de alterar esses endpoints.
