# Tarefas da Refatoração - code-smells-project

## T01 - Separar configuração, schema e seed do boot

- [x] **Status**: COMPLETED
- **Objetivo**: remover credenciais fixas, tornar init/seed explícitos e manter preparação determinística de testes.
- **Plano**: P01
- **Achados cobertos**: AP-02, AP-06B
- **Arquivos esperados**: `loja/config.py`, `loja/database.py`, `loja/__init__.py`, `tests/test_api.py`
- **Referências**: `mvc-guidelines.md` (Configuração/App), `refactoring-playbook.md` §1, relatório e plano
- **Pré-condições**: confirmação APPROVED; suíte-base verde
- **Passos**: separar `init_database` de `seed_database`; registrar CLI; condicionar auto-init somente a testes/config explícita; provisionar admin apenas por configuração externa; adaptar fixture de teste.
- **Validação**: CLI contra banco temporário, busca das senhas removidas e `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`.
- **Critério de aceite**: boot padrão não executa seed/DDL; não há senha runtime literal; testes continuam verdes.
- **Reversão/recuperação**: restaurar somente os arquivos desta tarefa via patch inverso; manter banco temporário fora do repositório.

## T02 - Adicionar migração e constraints de integridade

- [x] **Status**: COMPLETED
- **Objetivo**: garantir unicidade de email e relações consistentes sem descartar dados silenciosamente.
- **Plano**: P02
- **Achados cobertos**: AP-06A
- **Arquivos esperados**: `loja/database.py`, `loja/repositories/user_repository.py`, `loja/services/user_service.py`, `tests/test_api.py`
- **Referências**: `mvc-guidelines.md` (Repositories), `refactoring-playbook.md` §2/§4, plano P02
- **Pré-condições**: T01 COMPLETED
- **Passos**: criar schema versionado/upgrade transacional; adicionar `UNIQUE` case-insensitive e FKs; traduzir conflito de email para erro de domínio; testar base nova e legado válido.
- **Validação**: testes de constraints/migração e suíte completa.
- **Critério de aceite**: duplicidade é rejeitada como 409; FKs estão ativas; migração preserva dados válidos.
- **Reversão/recuperação**: falha de migração deve executar rollback e conservar tabelas legadas.

## T03 - Consolidar soft delete de produto

- [x] **Status**: COMPLETED
- **Objetivo**: dar comportamento efetivo ao campo `ativo` e preservar histórico.
- **Plano**: P02
- **Achados cobertos**: AP-15, AP-06A
- **Arquivos esperados**: `loja/models.py`, `loja/repositories/product_repository.py`, `loja/repositories/order_repository.py`, `tests/test_api.py`
- **Referências**: `mvc-guidelines.md` (Models/Repositories), plano D06
- **Pré-condições**: T02 COMPLETED
- **Passos**: filtrar produtos ativos; substituir delete físico por update; impedir uso de inativos em novos pedidos; preservar itens históricos.
- **Validação**: CRUD, busca, pedido e leitura de histórico; suíte completa.
- **Critério de aceite**: endpoint DELETE mantém 200; produto fica no banco com `ativo=0`, retorna 404 no catálogo e histórico permanece.
- **Reversão/recuperação**: reverter queries/repository sem alterar schema.

## T04 - Nomear e testar a política de desconto

- [x] **Status**: COMPLETED
- **Objetivo**: substituir números mágicos por política explícita sem alterar resultados.
- **Plano**: P03
- **Achados cobertos**: AP-14
- **Arquivos esperados**: `loja/services/report_service.py`, `tests/test_api.py`
- **Referências**: `refactoring-playbook.md` §9 e mapeamento AP-14
- **Pré-condições**: T03 COMPLETED
- **Passos**: criar constantes/faixas imutáveis; simplificar cálculo; adicionar testes de fronteira.
- **Validação**: testes unitários dos limites e suíte completa.
- **Critério de aceite**: resultados abaixo/nos/acima dos três patamares permanecem equivalentes.
- **Reversão/recuperação**: restaurar função anterior se equivalência falhar.

## T05 - Criar middleware de identidade e configuração segura de CORS/cookie

- [x] **Status**: COMPLETED
- **Objetivo**: introduzir autenticação reutilizável sem engrossar views/controllers.
- **Plano**: P04
- **Achados cobertos**: AP-03, AP-08
- **Arquivos esperados**: `loja/config.py`, `loja/middlewares/__init__.py`, `loja/middlewares/auth.py`, `loja/__init__.py`, `loja/views/user_routes.py`
- **Referências**: `mvc-guidelines.md` (Middlewares), `refactoring-playbook.md` §3/§8
- **Pré-condições**: T04 COMPLETED
- **Passos**: definir sessão segura; configurar CORS por allowlist; fazer login estabelecer principal; criar decorators de autenticação/papel/ownership.
- **Validação**: testes focados de sessão e guards, depois suíte completa antes de aplicar guards às demais rotas.
- **Critério de aceite**: sessão assinada contém apenas principal mínimo; guard produz 401/403 centralizados; CORS não é global por padrão.
- **Reversão/recuperação**: remover registro/uso do middleware mantendo login antigo temporariamente.

## T06 - Aplicar guards e ownership aos endpoints auditados

- [x] **Status**: COMPLETED
- **Objetivo**: bloquear mutações e enumeração indevidas, preservando sucesso autenticado.
- **Plano**: P04
- **Achados cobertos**: AP-03, AP-08
- **Arquivos esperados**: views de produto/usuário/pedido, `loja/controllers/order_controller.py`, `loja/services/order_service.py`, `tests/test_api.py`
- **Referências**: `mvc-guidelines.md` (Views/Services), plano de contratos P04
- **Pré-condições**: T05 COMPLETED
- **Passos**: proteger mutações por admin; limitar usuários/pedidos por admin/owner; validar owner ao criar pedido; adaptar testes e adicionar matriz 401/403/2xx.
- **Validação**: suíte completa e inspeção das 19 rotas.
- **Critério de aceite**: anônimo não lê PII nem muta domínio; cliente não acessa outro cliente; admin preserva fluxos existentes.
- **Reversão/recuperação**: remover decorators por domínio se houver regressão, mantendo middleware isolado.

## T07 - Atualizar documentação e executar validação final

- [x] **Status**: COMPLETED
- **Objetivo**: documentar operação segura, limpar resíduos e provar inicialização/contratos/arquitetura.
- **Plano**: P05
- **Achados cobertos**: AP-02, AP-03, AP-08, AP-06A, AP-06B, AP-14, AP-15
- **Arquivos esperados**: `README.md`, `reports/.refactor-arch/validation-report.md`, `STATE.md`
- **Referências**: `validation-checklist.md`, relatório, plano e tarefas
- **Pré-condições**: T01-T06 COMPLETED
- **Passos**: atualizar comandos/configuração; conferir imports e padrões; rodar CLI, suíte, startup controlado, fumaça HTTP e diff final.
- **Validação**: checklist completo da skill.
- **Critério de aceite**: aplicação inicia; 19 rotas permanecem registradas; testes e fumaça passam; nenhum CRITICAL/HIGH auditado permanece aberto.
- **Reversão/recuperação**: registrar qualquer limitação como PARTIAL sem mascarar falhas.

## Cobertura

- Etapas cobertas: P01 (T01), P02 (T02-T03), P03 (T04), P04 (T05-T06), P05 (T07).
- Achados cobertos: AP-02 (T01/T07), AP-03 (T05-T07), AP-08 (T05-T07), AP-06A (T02/T03/T07), AP-06B (T01/T07), AP-14 (T04/T07), AP-15 (T03/T07).
- Nenhum achado aprovado ficou sem decisão, tarefa ou validação.
