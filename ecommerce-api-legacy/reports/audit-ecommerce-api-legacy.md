# Relatório de Auditoria Arquitetural - ecommerce-api-legacy

**Gerado em**: 2026-07-11 21:40:31 -03  
**Caminho do projeto**: `.`  
**Stack**: JavaScript/CommonJS + Node.js + Express 4 + SQLite  
**Arquivos analisados**: 28 arquivos JavaScript relevantes  
**LOC aproximado**: 935 (aplicação e testes)  
**Domínio**: LMS/e-commerce de cursos com checkout, matrículas, pagamentos e relatório financeiro  
**Arquitetura atual**: MVC em camadas, com services, repositories, middlewares e raiz de composição  
**Estado do fluxo de trabalho**: `reports/.refactor-arch/STATE.md`

## Conclusão executiva

**Não é necessária uma nova refatoração para MVC.** A estrutura e as responsabilidades reais já estão adequadamente separadas: as rotas são declarativas, controllers adaptam HTTP, services coordenam regras, repositories isolam SQL parametrizado e `server.js` atua como raiz de composição.

Foram encontrados riscos residuais de manutenção e comportamento, mas nenhum `CRITICAL` ou `HIGH` e nenhuma violação estrutural que justifique a Fase 3 de refatoração MVC. Os itens abaixo podem ser tratados como melhorias incrementais separadas, com prioridade para a dependência SQLite descontinuada e para a idempotência do checkout.

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 5 |
| LOW | 2 |

Total de achados: 7

Há mais de cinco achados porque existe evidência concreta para riscos residuais. A ausência de achados `CRITICAL`/`HIGH` é deliberada: nenhum foi comprovado e problemas não foram promovidos artificialmente.

## Visão Arquitetural

- Ponto de entrada e raiz de composição: `src/server.js`.
- Camada de rotas/views HTTP: `src/routes/*.js`.
- Controllers: `src/controllers/*.js`.
- Regras de negócio: `src/services/*.js`.
- Validação de entrada: `src/validators/checkoutValidator.js` e validação pequena em `src/controllers/userController.js`.
- Camada de dados/models: `src/repositories/*.js` e `src/db/*.js`.
- Preocupações transversais: `src/middlewares/*.js` e `src/errors/AppError.js`.
- Principal risco arquitetural: não há risco estrutural alto; o maior risco técnico é o driver `sqlite3` descontinuado, encapsulado pela camada de dados existente.

## Controles verificados sem achados

- SQL de entrada externa usa placeholders e parâmetros; não foi encontrada concatenação insegura.
- Não há segredos fixados no código; a chave administrativa vem de `ADMIN_API_KEY`.
- Rotas administrativas de relatório e exclusão usam `adminAuth`.
- Senhas usam `crypto.scrypt`, salt aleatório e comparação de tempo constante.
- Respostas e logs não expõem senha, hash, cartão, chave ou stack trace.
- Relatório financeiro usa um único `JOIN`, sem N+1.
- Banco e dependências são injetados; não existe estado global mutável relevante.
- Não há SQL em routes/controllers nem regra pesada dentro dos adaptadores HTTP.

## Achados

### MEDIUM Driver SQLite oficialmente descontinuado

- **ID**: AP-13A
- **Arquivo**: `package.json:10-13`; `src/db/connection.js:1-5`
- **Evidência**: o projeto depende de `sqlite3` 5.x e importa diretamente esse driver no adaptador de conexão. O repositório oficial identifica `node-sqlite3` como descontinuado e sem manutenção.
- **Descrição**: a API local funciona, mas a dependência nativa não recebe manutenção futura. O risco é parcialmente contido porque o restante da aplicação acessa o banco por repositories e pelo helper `src/db/sqlite.js`.
- **Impacto**: incompatibilidades futuras de Node.js, ausência de correções e maior custo de instalação/suporte.
- **Recomendação**: definir primeiro a versão mínima de Node.js e substituir apenas o adaptador de persistência por `node:sqlite` ou outro driver ativamente mantido, preservando os contratos dos repositories.
- **Padrão de refatoração**: substituição de adapter/repository.
- **Confiança**: Alta.
- **Fonte oficial**: [repositório node-sqlite3](https://github.com/TryGhost/node-sqlite3); [documentação `node:sqlite`](https://nodejs.org/api/sqlite.html).

### MEDIUM Checkout não possui proteção contra repetição

- **ID**: AP-11A
- **Arquivo**: `src/services/checkoutService.js:42-67`; `src/db/initialize.js:20-34`
- **Evidência**: cada checkout aprovado cria incondicionalmente uma nova matrícula e um novo pagamento. O schema não possui unicidade para `(user_id, course_id)` nem chave de idempotência.
- **Descrição**: repetir a mesma requisição — inclusive por retry de rede — gera matrículas e pagamentos duplicados para o mesmo usuário e curso.
- **Impacto**: duplicidade de dados e potencial cobrança repetida quando a simulação for substituída por um gateway real.
- **Recomendação**: decidir a regra de rematrícula; se duplicidade não for válida, impor uma restrição no banco e/ou aceitar uma chave de idempotência, tratando conflito de modo explícito.
- **Padrão de refatoração**: invariantes no service com garantia no repository/schema.
- **Confiança**: Alta quanto ao comportamento; Média quanto à regra desejada, não documentada.

### MEDIUM Política de senha aceita qualquer valor não vazio

- **ID**: AP-11B
- **Arquivo**: `src/validators/checkoutValidator.js:15-29`; `src/services/passwordService.js:7-14`
- **Evidência**: a borda valida apenas que `pwd` não seja vazio; o serviço de hash repete somente essa condição. O exemplo de pagamento recusado em `api.http:21-25` usa a senha `123`, que passa na validação.
- **Descrição**: o armazenamento criptográfico é forte, porém a política de criação de credencial é incompleta.
- **Impacto**: contas podem ser criadas com senhas triviais, reduzindo a segurança do domínio caso autenticação de usuários seja adicionada ou já exista fora do escopo analisado.
- **Recomendação**: centralizar uma política documentada de tamanho mínimo/máximo e rejeição de entradas excessivas; manter `scrypt` para armazenamento.
- **Padrão de refatoração**: validator/schema na fronteira.
- **Confiança**: Alta.

### MEDIUM Inicialização do servidor não confirma sucesso nem trata erro de bind

- **ID**: AP-12A
- **Arquivo**: `src/server.js:56-69`; `test/run.js:51-59`
- **Evidência**: `startServer` retorna imediatamente após `app.listen`, e o caminho principal registra que a API está rodando sem aguardar o evento `listening`. A própria suíte precisa aguardar esse evento. Não há listener de `error` para falhas como porta ocupada.
- **Descrição**: erros assíncronos de abertura da porta ficam fora do `catch` da inicialização, e a mensagem de sucesso pode anteceder a confirmação real.
- **Impacto**: falha de startup não controlada, observabilidade enganosa e possível conexão de banco deixada aberta em erro de bind.
- **Recomendação**: encapsular `listen` em Promise que resolva em `listening` e rejeite em `error`; fechar o banco quando o bind falhar e registrar encerramento gracioso.
- **Padrão de refatoração**: lifecycle explícito na raiz de composição.
- **Confiança**: Alta.

### MEDIUM Exclusão reporta sucesso para usuário inexistente

- **ID**: AP-12B
- **Arquivo**: `src/repositories/userRepository.js:22-24`; `src/services/userService.js:6-9`; `src/controllers/userController.js:17-18`
- **Evidência**: o helper retorna `changes`, mas `deleteById` entrega esse resultado a um service que o ignora e sempre retorna `Usuário deletado.`; o controller sempre responde 200.
- **Descrição**: a resposta não distingue uma exclusão efetiva de uma operação sem alvo.
- **Impacto**: clientes e auditoria operacional recebem confirmação falsa, dificultando reconciliação e diagnóstico.
- **Recomendação**: verificar `changes`; retornar 404/erro de domínio quando nenhum registro for removido, preservando 200 para exclusão efetiva.
- **Padrão de refatoração**: mapeamento consistente de resultado de repository para erro de domínio.
- **Confiança**: Alta.

### LOW Regra de pagamento simulada usa valor mágico

- **ID**: AP-14A
- **Arquivo**: `src/services/checkoutService.js:34-40`
- **Evidência**: qualquer cartão iniciado por `4` é tratado como pago e todos os demais como recusados; a regra está embutida no caso de uso.
- **Descrição**: a simulação é simples e não viola MVC, mas acopla o checkout a um gateway fictício e a um valor mágico.
- **Impacto**: substituição futura do provedor exigirá mudança no service e testes; a regra pode ser confundida com autorização real.
- **Recomendação**: quando houver integração real, injetar um `paymentGateway`; até lá, nomear explicitamente o simulador e a regra para deixar o limite claro.
- **Padrão de refatoração**: extrair adapter de integração.
- **Confiança**: Alta.

### LOW Rotas desconhecidas fogem do contrato JSON de erros

- **ID**: AP-12C
- **Arquivo**: `src/app.js:15-19`; `src/middlewares/errorHandler.js:3-20`
- **Evidência**: após as três rotas, somente o middleware de erro é registrado. Não há middleware de `not found`; uma URL desconhecida cai na resposta 404 padrão do Express, em HTML.
- **Descrição**: erros conhecidos usam `{ error, code }`, mas endpoints inexistentes não passam pelo mesmo contrato.
- **Impacto**: clientes da API precisam tratar formatos de erro diferentes.
- **Recomendação**: adicionar um middleware 404 que encaminhe `AppError` antes do `errorHandler`.
- **Padrão de refatoração**: middleware transversal de erro.
- **Confiança**: Alta.

## Achados de APIs Obsoletas

| API/dependência | Localização | Uso atual | Equivalente moderno | Confiança |
|---|---|---|---|---|
| `sqlite3` / `node-sqlite3` | `package.json:12`, `src/db/connection.js:1-5` | driver callback nativo, versão resolvida 5.1.7 | `node:sqlite` para uma versão de Node compatível ou driver mantido | Alta |

O `node-sqlite3` está oficialmente descontinuado. As APIs próprias usadas no código (`Buffer.from`, `crypto.scrypt`, `crypto.timingSafeEqual`, `express.json`) não estão obsoletas. Express 4.22.1 está em manutenção, não em uso de API removida; a política oficial incentiva migração para Express 5, mas essa atualização não é necessária para corrigir MVC e deve ser tratada como modernização separada. Consulte a [linha de suporte oficial do Express](https://expressjs.com/en/blog/2025/03/31-v5-1-latest-release/).

## Alvos de Refatoração MVC

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|
| Estrutura MVC | `src/routes`, `src/controllers`, `src/services`, `src/repositories` | Manter como está | Separação adequada; nenhuma reestruturação necessária |
| Adapter SQLite | `src/db/connection.js`, `src/db/sqlite.js` | Mesmo limite de persistência, com driver mantido | Modernização de dependência, não correção MVC |
| Invariantes de checkout | `checkoutValidator.js`, `checkoutService.js`, schema | Manter nas camadas existentes | Fortalecer senha e idempotência sem mover responsabilidades |
| Ciclo de vida HTTP | `src/server.js` | Manter na raiz de composição | Tratar bind e encerramento explicitamente |

## Plano de Validação para uma eventual melhoria incremental

- Comando de inicialização: `ADMIN_API_KEY="uma-chave-local-segura" npm start`.
- Endpoints de fumaça: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`.
- Comando de testes: `npm test` ou, neste ambiente, `"/mnt/c/Program Files/nodejs/node.exe" test/run.js` com interoperabilidade WSL habilitada.
- Preparação de dados: nenhuma; SQLite em memória e seeds automáticos.
- Resultado atual: `PASS: regressão funcional, segurança e arquitetura MVC`.
- Arquivo de estado: `reports/.refactor-arch/STATE.md`.

## Pré-condições da Fase 3

- O humano revisou este relatório.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints está registrado em `STATE.md`.
- Caso a Fase 3 seja aprovada apesar da recomendação, ela deve tratar somente achados selecionados e preservar a estrutura MVC já adequada.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
