# Tarefas da Refatoração MVC - ecommerce-api-legacy

- [x] T01 - Criar configuração e base de erros
  Objetivo: extrair configuração de ambiente, erro tipado e middleware central.
  Plano: P01.
  Achados cobertos: AP-02, AP-12.
  Arquivos esperados: `src/config/index.js`, `src/errors/AppError.js`, `src/middlewares/errorHandler.js`.
  Referências: `mvc-guidelines.md`, playbook itens 1 e 8, relatório.
  Pré-condições: confirmação aprovada; nenhum segredo padrão.
  Passos de implementação: criar config; criar `AppError`; mapear erro seguro no middleware.
  Validação: carregar módulos com Node e revisar ausência de segredo.
  Critério de aceite: porta padrão 3000, admin key somente do ambiente e erros sem detalhe interno.
  Reversão/recuperação: arquivos novos podem permanecer desacoplados até composição.

- [x] T02 - Criar adapter SQLite, schema e inicialização
  Objetivo: encapsular callbacks, habilitar foreign keys e seed seguro.
  Plano: P03.
  Achados cobertos: AP-06, AP-07, AP-12.
  Arquivos esperados: `src/db/connection.js`, `src/db/sqlite.js`, `src/db/initialize.js`.
  Referências: guidelines de repositories, playbook itens 4 e 6.
  Pré-condições: T01 concluída; password service mínimo poderá ser criado junto do seed se necessário.
  Passos de implementação: wrappers Promise; transação; schema com FKs; seeds com hash injetado.
  Validação: criar banco, consultar tabelas e verificar hash/foreign keys.
  Critério de aceite: inicialização atômica sem senha em texto puro.
  Reversão/recuperação: arquivos novos não substituem o boot até T09.

- [x] T03 - Extrair repositories e consulta financeira
  Objetivo: isolar todo SQL operacional e substituir N+1 por uma consulta.
  Plano: P03.
  Achados cobertos: AP-04, AP-06, AP-09.
  Arquivos esperados: `src/repositories/*Repository.js`.
  Referências: guidelines e playbook itens 4 e 5.
  Pré-condições: T02 concluída.
  Passos de implementação: repositories de usuário, curso, matrícula, pagamento, auditoria e relatório.
  Validação: busca estática de SQL fora de db/repositories e execução das consultas.
  Critério de aceite: services não precisarão conhecer SQL; relatório usa um result set.
  Reversão/recuperação: composição antiga permanece ativa até T09.

- [x] T04 - Implementar segurança local e services de domínio
  Objetivo: scrypt com salt, checkout transacional, relatório agregado e exclusão consistente.
  Plano: P02, P04.
  Achados cobertos: AP-05, AP-06, AP-07, AP-08, AP-09, AP-10, AP-14.
  Arquivos esperados: `src/services/passwordService.js`, `checkoutService.js`, `financialReportService.js`, `userService.js`.
  Referências: playbook itens 3, 5 e 6; plano ADR-02/03/06.
  Pré-condições: T03 concluída.
  Passos de implementação: regras nomeadas; transação; nenhum log sensível; remoção conceitual do cache.
  Validação: testes diretos de services e inspeção de logs.
  Critério de aceite: services sem Express e checkout atômico.
  Reversão/recuperação: serviços novos ainda não roteados.

- [x] T05 - Extrair validator e controllers
  Objetivo: preservar a borda HTTP com validação central e controllers finos.
  Plano: P05.
  Achados cobertos: AP-04, AP-05, AP-11, AP-12, AP-14.
  Arquivos esperados: `src/validators/checkoutValidator.js`, `src/controllers/*Controller.js`.
  Referências: playbook itens 3, 8 e 9.
  Pré-condições: T04 concluída.
  Passos de implementação: normalizar DTO; controllers async; encaminhar erros ao middleware.
  Validação: objetos mock de request/response e revisão sem SQL.
  Critério de aceite: controllers apenas adaptam HTTP e mantêm status/payload essencial.
  Reversão/recuperação: controllers não registrados até T08/T09.

- [x] T06 - Criar autenticação administrativa e rotas
  Objetivo: proteger operações sensíveis e declarar rotas finas.
  Plano: P06.
  Achados cobertos: AP-03, AP-04, AP-12.
  Arquivos esperados: `src/middlewares/adminAuth.js`, `src/routes/*Routes.js`.
  Referências: guidelines de routes/middlewares e relatório AP-03.
  Pré-condições: T05 concluída; política ADR-04/05.
  Passos de implementação: middleware com comparação timing-safe; routers por domínio.
  Validação: sem chave 503/401 conforme configuração; chave válida permite acesso; routes sem SQL.
  Critério de aceite: métodos/caminhos preservados e protegidos.
  Reversão/recuperação: routers novos ainda podem ser desconectados.

- [x] T07 - Criar app factory e raiz de composição
  Objetivo: substituir `AppManager` por dependências explícitas e separar `listen`.
  Plano: P07.
  Achados cobertos: AP-04.
  Arquivos esperados: `src/app.js`, `src/server.js`, `package.json`.
  Referências: estrutura Express das guidelines.
  Pré-condições: T06 concluída.
  Passos de implementação: app factory; composition root; aguardar seed antes de escutar; preservar `npm start`.
  Validação: inicialização e registro dos três endpoints.
  Critério de aceite: ponto de entrada pequeno, previsível e testável.
  Reversão/recuperação: `AppManager` só será removido após este boot validar.

- [x] T08 - Remover legado e documentar operação
  Objetivo: apagar Objeto Deus/estado morto e documentar autenticação/configuração.
  Plano: P08.
  Achados cobertos: AP-02, AP-04, AP-10, AP-15.
  Arquivos esperados: remoção de `src/AppManager.js`, `src/utils.js`; atualização de `README.md`, `api.http`.
  Referências: playbook item 4 e checklist arquitetural.
  Pré-condições: T07 validada.
  Passos de implementação: confirmar ausência de imports; remover legado; atualizar exemplos.
  Validação: busca por nomes/segredos antigos e novo boot.
  Critério de aceite: nenhum import morto, segredo, cache global ou arquivo Deus.
  Reversão/recuperação: restaurar arquivos apenas se ainda houver consumidor detectado.

- [x] T09 - Adicionar regressão automatizada e executar validação final
  Objetivo: cobrir boot, contratos, segurança, integridade e arquitetura.
  Plano: P09.
  Achados cobertos: AP-02, AP-03, AP-04, AP-05, AP-06, AP-07, AP-08, AP-09, AP-10, AP-11, AP-12, AP-14, AP-15.
  Arquivos esperados: `test/app.test.js`, `package.json`, `reports/.refactor-arch/validation-report.md`.
  Referências: `validation-checklist.md`, relatório e plano.
  Pré-condições: T08 concluída.
  Passos de implementação: testes com módulos nativos; smoke HTTP; varredura arquitetural; relatório final.
  Validação: `npm test`, `npm start` controlado e requisições aos três endpoints.
  Critério de aceite: testes passam ou limitação externa é registrada com estado PARTIAL.
  Reversão/recuperação: manter testes falhos registrados para correção, sem mascarar resultado.
