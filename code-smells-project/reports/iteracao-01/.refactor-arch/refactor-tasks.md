# Tarefas de Refatoracao MVC - code-smells-project

- [x] T01 - Criar fundacao, configuracao, banco e DTOs
  Objetivo: criar o pacote `loja`, configuracao por ambiente, excecoes, models/DTOs seguros e conexao SQLite por contexto.
  Plano: P01
  Achados cobertos: AP-02, AP-08, AP-10, AP-14
  Arquivos esperados: `loja/__init__.py`, `loja/config.py`, `loja/database.py`, `loja/errors.py`, `loja/models.py`
  Referencias: `mvc-guidelines.md` (Configuracao/Models), playbook 1 e 7
  Pre-condicoes: Fase 3 aprovada; codigo-fonte liberado.
  Passos de implementacao: criar estrutura; ler ambiente; gerar segredo de desenvolvimento; implementar `g`/teardown; schema/seed com hash; DTOs sem credencial.
  Validacao: `PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q loja` e inicializacao do schema em banco temporario.
  Criterio de aceite: nenhum segredo literal; conexao fechada no teardown; seed armazena hash.
  Reversao/recuperacao: corrigir modulo isolado antes de iniciar repositories.

- [x] T02 - Extrair repositories parametrizados
  Objetivo: criar repositories de produto, usuario, pedido e relatorio sem SQL concatenado e sem HTTP.
  Plano: P02
  Achados cobertos: AP-01, AP-04, AP-06, AP-09, AP-10
  Arquivos esperados: `loja/repositories/__init__.py`, `product_repository.py`, `user_repository.py`, `order_repository.py`, `report_repository.py`
  Referencias: `mvc-guidelines.md` (Repositories), playbook 2, 4 e 5
  Pre-condicoes: T01 COMPLETED.
  Passos de implementacao: implementar CRUD parametrizado; consulta em lote de produtos; listagem de pedidos com joins; agregacao de relatorio.
  Validacao: compilacao e busca estatica por concatenacao junto a `execute`.
  Criterio de aceite: todo SQL recebe placeholders; listagem de pedidos nao consulta dentro de loops.
  Reversao/recuperacao: manter os novos modulos sem trocar consumidores ate validar.

- [x] T03 - Extrair services e validadores de dominio
  Objetivo: implementar casos de uso de produto, usuario, pedido, relatorio e administracao.
  Plano: P03
  Achados cobertos: AP-05, AP-06, AP-07, AP-11, AP-14
  Arquivos esperados: `loja/services/__init__.py`, `product_service.py`, `user_service.py`, `order_service.py`, `report_service.py`, `admin_service.py`
  Referencias: `mvc-guidelines.md` (Services), playbook 3, 6 e 9
  Pre-condicoes: T02 COMPLETED.
  Passos de implementacao: centralizar regras; hash e migracao de senha; transacao de pedido; restauracao de estoque; autorizacao admin.
  Validacao: compilacao e exercicio dos services com banco temporario.
  Criterio de aceite: services sem Flask HTTP; rollback em falhas compostas; senha nunca comparada em SQL.
  Reversao/recuperacao: corrigir caso de uso antes de expor nas rotas.

- [x] T04 - Montar controllers, views e application factory
  Objetivo: trocar adaptacao HTTP pelo MVC novo, registrar handlers e preservar os 19 endpoints.
  Plano: P04
  Achados cobertos: AP-01, AP-02, AP-03, AP-04, AP-05, AP-08, AP-12, AP-15
  Arquivos esperados: `loja/controllers/*.py`, `loja/views/*.py`, `loja/__init__.py`, `app.py`
  Referencias: `mvc-guidelines.md` (Controllers/Views/App/Middlewares), playbook 3, 7 e 8
  Pre-condicoes: T03 COMPLETED.
  Passos de implementacao: controllers finos; Blueprints por dominio; erros centralizados; admin seguro; factory e entrypoint.
  Validacao: importar `app`, contar 19 regras e executar smoke via test client em banco temporario.
  Criterio de aceite: views sem SQL/regra pesada; 19 caminhos registrados; respostas sensiveis sanitizadas.
  Reversao/recuperacao: modulos legados ainda permanecem disponiveis ate T05.

- [x] T05 - Adicionar regressao e remover estrutura legada
  Objetivo: congelar contratos, documentar operacao segura e remover modulos mortos.
  Plano: P05
  Achados cobertos: AP-02, AP-03, AP-07, AP-08, AP-15; regressao AP-01 a AP-15
  Arquivos esperados: `tests/test_api.py`, `README.md`; remocao de `controllers.py`, `database.py`, `models.py`
  Referencias: `validation-checklist.md`, relatorio de auditoria e plano aprovado
  Pre-condicoes: T04 COMPLETED.
  Passos de implementacao: testes dos 19 endpoints/seguranca; documentar env vars; remover modulos sem consumidores.
  Validacao: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` e varreduras arquiteturais.
  Criterio de aceite: suite passa; nenhum modulo legado importado; nenhum artefato de banco/cache no repositorio.
  Reversao/recuperacao: restaurar temporariamente apenas o modulo ainda importado e corrigir consumidor.

- [x] T06 - Validar inicializacao, HTTP e cobertura final
  Objetivo: executar checklist completo e registrar evidencias finais.
  Plano: P06
  Achados cobertos: AP-01 a AP-15
  Arquivos esperados: `reports/.refactor-arch/validation-report.md`, `reports/.refactor-arch/STATE.md`
  Referencias: `validation-checklist.md`, `workflow-state.md`, plano e tarefas
  Pre-condicoes: T05 COMPLETED.
  Passos de implementacao: compile/test; subir servidor em porta livre com DB temporario; testar HTTP; scans; conferir diff.
  Validacao: comandos registrados no relatorio de validacao.
  Criterio de aceite: app inicia; endpoints principais respondem; todos os achados FIX possuem evidencia.
  Reversao/recuperacao: marcar FAILED e corrigir somente falhas pequenas antes de repetir.
