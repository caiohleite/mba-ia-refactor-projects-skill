# Tarefas da Refatoração MVC - task-manager-api

- [x] T01 - Extrair configuração, relógio UTC e erros centrais
  Objetivo: criar configuração por ambiente, exceções de aplicação e handler Flask.
  Plano: P01.
  Achados cobertos: AP-02, AP-12, AP-13.
  Arquivos esperados: `config.py`, `exceptions.py`, `utils/time.py`, `middlewares/__init__.py`, `middlewares/error_handler.py`.
  Referências: `mvc-guidelines.md`, padrões 1, 8 e 10 do playbook.
  Pré-condições: aprovação registrada e plano salvo.
  Passos de implementação: criar settings sem segredo literal; criar `utc_now`; definir exceções tipadas; registrar handler reutilizável.
  Validação: parse AST/import dos novos módulos.
  Critério de aceite: módulos importam sem erro, segredos vêm do ambiente/geração segura e erros têm resposta JSON central.
  Reversão/recuperação: os novos módulos ainda não são consumidos; corrigir isoladamente antes de T02.

- [x] T02 - Enxugar models e criar schemas/DTOs seguros
  Objetivo: trocar hash de senha, remover serialização sensível do model e centralizar constantes, validação e saída.
  Plano: P02.
  Achados cobertos: AP-07, AP-08, AP-11, AP-13, AP-14.
  Arquivos esperados: `models/*.py`, `schemas/__init__.py`, `schemas/constants.py`, `schemas/validators.py`, `schemas/serializers.py`.
  Referências: padrões 6, 7, 9 e 10 do playbook; auditoria AP-07/AP-08/AP-11.
  Pré-condições: T01 completa.
  Passos de implementação: usar Werkzeug; suportar migração MD5; usar UTC explícito; criar validadores e DTOs preservando campos públicos não sensíveis.
  Validação: testes focados por comando Python e parse AST.
  Critério de aceite: nenhum DTO público contém senha, hash forte é gerado e payloads inválidos produzem exceções de domínio.
  Reversão/recuperação: restaurar consumo temporário via serializer, nunca reintroduzir `password` público.

- [x] T03 - Encapsular persistência em repositories
  Objetivo: remover queries/transações das futuras camadas HTTP e corrigir N+1/API legada.
  Plano: P02.
  Achados cobertos: AP-06, AP-09, AP-13, AP-14.
  Arquivos esperados: `repositories/__init__.py`, `task_repository.py`, `user_repository.py`, `category_repository.py`, `report_repository.py`.
  Referências: padrões 4, 5 e 10 do playbook.
  Pré-condições: T02 completa.
  Passos de implementação: usar `db.session.get`, eager loading, agregações e métodos explícitos de persistência.
  Validação: parse/import e busca por `query.get` nos repositories.
  Critério de aceite: repositories cobrem todos os acessos existentes sem consulta dentro de loops de entidade.
  Reversão/recuperação: corrigir interface antes de conectá-la aos services.

- [x] T04 - Extrair services de domínio e autenticação
  Objetivo: implementar casos de uso de tarefas, usuários, categorias, relatórios e login fora do Flask.
  Plano: P03.
  Achados cobertos: AP-03, AP-05, AP-06, AP-07, AP-11.
  Arquivos esperados: `services/task_service.py`, `user_service.py`, `auth_service.py`, `category_service.py`, `report_service.py`.
  Referências: diretrizes MVC; padrões 3, 4, 6 e 9 do playbook.
  Pré-condições: T03 completa.
  Passos de implementação: orquestrar repositories, validar domínio, controlar commits/rollbacks e gerar/verificar token assinado.
  Validação: testes diretos dos principais casos de uso em banco em memória.
  Critério de aceite: services não importam Flask/request/jsonify e cobrem os fluxos de todos os endpoints.
  Reversão/recuperação: ajustar interfaces isoladamente antes de substituir rotas.

- [x] T05 - Implementar autenticação/autorização middleware
  Objetivo: carregar usuário por Bearer token e aplicar papéis às operações privilegiadas.
  Plano: P03.
  Achados cobertos: AP-03, AP-07, AP-12.
  Arquivos esperados: `middlewares/auth.py`, `middlewares/__init__.py`.
  Referências: auditoria AP-03/AP-07 e diretrizes de segurança.
  Pré-condições: T04 completa.
  Passos de implementação: criar decorators autenticado/papéis; preencher `g.current_user`; usar exceções centrais.
  Validação: teste de decorator para sem token, token inválido, papel insuficiente e admin.
  Critério de aceite: retornos 401/403 consistentes e token válido disponibiliza usuário.
  Reversão/recuperação: decorators só serão aplicados na T06.

- [x] T06 - Criar controllers e tornar rotas finas
  Objetivo: preservar os 22 caminhos enquanto separa HTTP, casos de uso e persistência.
  Plano: P04.
  Achados cobertos: AP-03, AP-04, AP-05, AP-06, AP-08, AP-12.
  Arquivos esperados: `controllers/*.py`, `routes/*.py`, novo `routes/category_routes.py`.
  Referências: padrões 3, 4, 7 e 8 do playbook; contrato em `STATE.md`.
  Pré-condições: T05 completa.
  Passos de implementação: controllers adaptam request/respostas; Blueprints delegam; aplicar decorators por risco; preservar códigos/campos não sensíveis.
  Validação: parse/import, mapa de URL com 22 contratos e varredura de `db`/`.query` em routes/controllers.
  Critério de aceite: nenhuma rota/controller acessa ORM e todos os métodos/caminhos permanecem registrados.
  Reversão/recuperação: corrigir domínio por domínio; não avançar à composição se o mapa divergir.

- [x] T07 - Atualizar composição, seed, notificação e limpeza
  Objetivo: ligar todas as camadas, preservar comandos e remover segredos/imports residuais.
  Plano: P05.
  Achados cobertos: AP-02, AP-04, AP-13, AP-14, AP-15.
  Arquivos esperados: `app.py`, `seed.py`, `services/notification_service.py`, `utils/helpers.py`.
  Referências: padrões 1, 4, 8, 9 e 10; diretrizes de composition root.
  Pré-condições: T06 completa.
  Passos de implementação: criar/register app factory, error handler e Blueprints; parametrizar SMTP; modernizar datas; limpar imports/helpers sem remover função usada.
  Validação: parse AST, import da app, boot controlado e busca por segredos/APIs legadas.
  Critério de aceite: `python app.py` e `seed.py` continuam válidos; aplicação inicia; nenhuma credencial fixa permanece.
  Reversão/recuperação: corrigir composition root sem desfazer camadas completas.

- [x] T08 - Criar testes de contrato e validar a refatoração
  Objetivo: cobrir boot, os 22 contratos, segurança e regressão arquitetural.
  Plano: P06.
  Achados cobertos: AP-02, AP-03, AP-04, AP-05, AP-06, AP-07, AP-08, AP-09, AP-11, AP-12, AP-13, AP-14, AP-15.
  Arquivos esperados: `tests/__init__.py`, `tests/test_api.py`, `reports/.refactor-arch/validation-report.md`.
  Referências: `validation-checklist.md`, auditoria, plano e contrato em `STATE.md`.
  Pré-condições: T07 completa e app importável.
  Passos de implementação: configurar SQLite em memória; semear fixtures; testar rotas públicas/protegidas e payloads; executar varredura arquitetural e boot.
  Validação: `venv/bin/python -m unittest discover -s tests -v` e smoke test de processo/cliente Flask.
  Critério de aceite: testes passam, 22 caminhos existem, críticos/altos corrigidos e relatório final salvo.
  Reversão/recuperação: registrar falha, corrigir somente o menor ajuste necessário e reexecutar.
