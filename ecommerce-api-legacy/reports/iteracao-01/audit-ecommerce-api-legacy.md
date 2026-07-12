# Relatório de Auditoria Arquitetural - ecommerce-api-legacy

**Gerado em**: 2026-07-11 20:32:22 -0300  
**Caminho do projeto**: `.`  
**Stack**: JavaScript (Node.js/CommonJS), Express 4.22.1 e sqlite3 5.1.7  
**Arquivos analisados**: 3  
**LOC aproximado**: 180  
**Domínio**: LMS com checkout, matrículas e pagamentos  
**Arquitetura atual**: monolito com Objeto Deus e ausência de camadas MVC reais  
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

- Ponto de entrada: `src/app.js`.
- Camada de rotas: incorporada ao método `AppManager.setupRoutes` em `src/AppManager.js`.
- Camada de dados/modelos: inexistente; schema, seeds e SQL ficam em `src/AppManager.js`.
- Locais com lógica de negócio: callbacks das rotas em `src/AppManager.js` e hashing/cache em `src/utils.js`.
- Pontos de integração/banco de dados: conexão SQLite em memória e simulação inline de gateway em `src/AppManager.js`.
- Principal risco arquitetural: operações financeiras e administrativas misturam HTTP, regra, persistência e dados sensíveis sem fronteiras de segurança ou transações.

## Achados

### CRITICAL Segredos de produção fixados no código

- **ID**: AP-02
- **Arquivo**: `src/utils.js:1-6`
- **Evidência**: configuração versionada contém usuário e senha de banco, chave de gateway marcada como live e usuário SMTP.
- **Descrição**: credenciais e chave de integração são constantes carregadas diretamente pela aplicação.
- **Impacto**: qualquer acesso ao repositório expõe segredos, impede rotação segura por ambiente e pode permitir acesso indevido a serviços externos.
- **Recomendação**: criar configuração central baseada em variáveis de ambiente, falhar com mensagem segura quando segredo obrigatório faltar e substituir/rotacionar os valores expostos.
- **Padrão de refatoração**: Configuration Object / Environment-based Configuration.
- **Confiança**: Alta

### CRITICAL Endpoints administrativos e destrutivos sem proteção

- **ID**: AP-03
- **Arquivo**: `src/AppManager.js:80-137`
- **Evidência**: o relatório financeiro e a exclusão de usuários são registrados sem middleware de autenticação ou autorização.
- **Descrição**: qualquer cliente com acesso à API pode consultar dados financeiros/agregados de alunos e excluir usuários por identificador.
- **Impacto**: exposição de informação sensível e alteração destrutiva sem controle de acesso ou trilha de autorização.
- **Recomendação**: introduzir middleware de autenticação e autorização por papel; proteger ambas as rotas e auditar operações destrutivas.
- **Padrão de refatoração**: Authentication/Authorization Middleware.
- **Confiança**: Alta

### CRITICAL Armazenamento de senha inseguro

- **ID**: AP-07
- **Arquivo**: `src/AppManager.js:12-18`; `src/AppManager.js:66-71`; `src/utils.js:17-23`
- **Evidência**: o seed grava a senha `123` em texto puro e novos usuários passam por uma função caseira que repete Base64 e trunca o resultado para dez caracteres.
- **Descrição**: Base64 não é função de derivação de senha e o resultado curto, determinístico e sem salt é trivialmente reversível/atacável.
- **Impacto**: comprometimento do banco expõe senhas imediatamente e pode facilitar reutilização de credenciais em outros sistemas.
- **Recomendação**: adotar `scrypt`, `bcrypt` ou `argon2` com salt e parâmetros adequados, normalizar o seed e encapsular hashing/verificação em serviço dedicado.
- **Padrão de refatoração**: Password Hasher Adapter.
- **Confiança**: Alta

### CRITICAL Vazamento de cartão e chave de pagamento em log

- **ID**: AP-08
- **Arquivo**: `src/AppManager.js:43-46`
- **Evidência**: o fluxo imprime o número integral recebido em `card` junto da chave live configurada para o gateway.
- **Descrição**: dados de pagamento e credencial de integração são enviados ao console sem mascaramento.
- **Impacto**: logs podem expor número de cartão e segredo operacional, ampliando risco de fraude e não conformidade.
- **Recomendação**: nunca registrar PAN ou chaves; usar logger estruturado com redação de campos sensíveis e somente identificadores/token de transação.
- **Padrão de refatoração**: Secure Logging / Sensitive-data Redaction.
- **Confiança**: Alta

### HIGH `AppManager` é um Objeto Deus

- **ID**: AP-04
- **Arquivo**: `src/AppManager.js:4-139`
- **Evidência**: uma única classe abre o banco, cria schema e seeds, registra rotas, valida requests, executa regras de pagamento, persiste entidades, gera relatórios e serializa respostas.
- **Descrição**: a classe possui múltiplos motivos para mudar e concentra praticamente toda a aplicação.
- **Impacto**: alto acoplamento, baixa testabilidade e grande risco de regressão em qualquer evolução.
- **Recomendação**: manter uma raiz de composição pequena e extrair routes/views, controllers, services e repositories/models por domínio.
- **Padrão de refatoração**: Extract Class + MVC Composition Root.
- **Confiança**: Alta

### HIGH Regra de checkout pesada dentro da rota

- **ID**: AP-05
- **Arquivo**: `src/AppManager.js:28-78`
- **Evidência**: o manipulador interpreta payload, valida curso/usuário, decide status de pagamento, cria usuário, matrícula, pagamento e log de auditoria.
- **Descrição**: o caso de uso completo está acoplado a `req`, `res` e callbacks de SQLite.
- **Impacto**: regras não podem ser testadas isoladamente ou reutilizadas e mudanças de transporte/banco afetam o fluxo de negócio.
- **Recomendação**: criar `CheckoutController` fino e `CheckoutService` para orquestrar o caso de uso por dependências injetadas.
- **Padrão de refatoração**: Extract Service / Thin Controller.
- **Confiança**: Alta

### HIGH Persistência sem fronteira transacional e integridade referencial

- **ID**: AP-06
- **Arquivo**: `src/AppManager.js:12-16`; `src/AppManager.js:50-61`; `src/AppManager.js:131-136`
- **Evidência**: tabelas não declaram chaves estrangeiras; matrícula, pagamento e auditoria são gravados em callbacks independentes sem rollback; a exclusão remove apenas o usuário e a própria resposta admite dados órfãos.
- **Descrição**: detalhes SQL e consistência do caso de uso ficam misturados à rota, sem transação atômica nem política de exclusão.
- **Impacto**: falha intermediária deixa checkout parcial e a exclusão corrompe relações lógicas, prejudicando relatórios e manutenção.
- **Recomendação**: introduzir repositories, transação no serviço de checkout, constraints de chave estrangeira e uma política explícita de restrição/cascata para exclusão.
- **Padrão de refatoração**: Repository + Unit of Work.
- **Confiança**: Alta

### MEDIUM Consultas N+1 no relatório financeiro

- **ID**: AP-09
- **Arquivo**: `src/AppManager.js:83-127`
- **Evidência**: após listar cursos, o código consulta matrículas por curso e depois usuário e pagamento para cada matrícula.
- **Descrição**: o total de consultas cresce como `1 + cursos + 2 × matrículas`, com coordenação manual por contadores.
- **Impacto**: latência e uso de banco crescem rapidamente com o volume, além de aumentar a complexidade e a chance de respostas incompletas.
- **Recomendação**: consolidar o relatório em consulta com JOIN/agregação ou consultas em lote encapsuladas em repository.
- **Padrão de refatoração**: Query Object / Batch Loading.
- **Confiança**: Alta

### MEDIUM Estado global mutável para cache

- **ID**: AP-10
- **Arquivo**: `src/utils.js:9-15`
- **Evidência**: `globalCache` é um objeto mutável no escopo do módulo e `logAndCache` o altera diretamente.
- **Descrição**: o estado não tem ciclo de vida, limites, invalidação ou interface injetável.
- **Impacto**: testes interferem entre si, o consumo de memória pode crescer sem controle e múltiplas instâncias ficam inconsistentes.
- **Recomendação**: encapsular cache atrás de interface injetada, definir ciclo de vida/limites ou removê-lo se não houver requisito funcional.
- **Padrão de refatoração**: Dependency Injection / Cache Adapter.
- **Confiança**: Alta

### MEDIUM Validação de entrada parcial e acoplada ao handler

- **ID**: AP-11
- **Arquivo**: `src/AppManager.js:28-35`
- **Evidência**: apenas presença de quatro campos é verificada; senha não é obrigatória, e-mail, curso e cartão não têm tipo/formato validados, e os nomes abreviados são interpretados manualmente.
- **Descrição**: regras de entrada e defaults ficam espalhados no fluxo HTTP, incluindo senha padrão posterior.
- **Impacto**: payloads inválidos atravessam camadas, geram respostas inconsistentes e ampliam risco de dados incorretos.
- **Recomendação**: preservar o contrato externo, mas centralizar parsing e validação em schema/DTO antes do controller chamar o serviço.
- **Padrão de refatoração**: Request DTO / Validation Schema.
- **Confiança**: Alta

### MEDIUM Tratamento de erros inconsistente ou ignorado

- **ID**: AP-12
- **Arquivo**: `src/AppManager.js:37-77`; `src/AppManager.js:83-136`
- **Evidência**: alguns callbacks convertem qualquer erro em texto genérico, enquanto erros ao inserir auditoria, buscar matrículas/usuários/pagamentos e excluir usuário são ignorados; callbacks assumem dados existentes.
- **Descrição**: não há política central de erros, rollback ou distinção consistente entre falha técnica, validação e recurso ausente.
- **Impacto**: requisições podem responder sucesso apesar de falha, lançar exceções por dados indefinidos ou deixar operações parciais.
- **Recomendação**: adaptar SQLite para Promises, criar erros de aplicação e middleware central, garantindo rollback e uma única resposta por requisição.
- **Padrão de refatoração**: Error Boundary Middleware / Application Errors.
- **Confiança**: Alta

### LOW Nomes obscuros e valores mágicos no checkout

- **ID**: AP-14
- **Arquivo**: `src/AppManager.js:29-46`; `src/AppManager.js:66-69`
- **Evidência**: variáveis `u`, `e`, `p`, `cid`, `cc` e o prefixo `4`, status textuais e senha padrão aparecem diretamente na regra.
- **Descrição**: abreviações e literais escondem conceitos de domínio e condições relevantes.
- **Impacto**: piora legibilidade e aumenta o risco de divergência ao alterar regras.
- **Recomendação**: mapear o payload para nomes de domínio e extrair constantes/políticas para status e simulação de gateway.
- **Padrão de refatoração**: Rename Variable + Replace Magic Value with Constant/Policy.
- **Confiança**: Alta

### LOW Importação e estado residual não usados

- **ID**: AP-15
- **Arquivo**: `src/AppManager.js:2`; `src/utils.js:10`; `src/utils.js:25`
- **Evidência**: `totalRevenue` é declarado, exportado e importado, mas nunca é lido nem atualizado.
- **Descrição**: responsabilidade residual sugere uma implementação abandonada de agregação global.
- **Impacto**: gera ruído e confusão sobre a fonte oficial da receita.
- **Recomendação**: remover o estado/import após confirmar que a consulta/repository do relatório é a única fonte de agregação.
- **Padrão de refatoração**: Remove Dead Code.
- **Confiança**: Alta

## Achados de APIs Obsoletas

Nenhum uso direto de API obsoleta foi identificado no código-fonte com as evidências disponíveis. `Buffer.from` já é a API moderna; o problema de `badCrypto` é criptográfico, não de obsolescência. Há dependências transitivas marcadas como deprecated no lockfile, mas elas não constituem uso direto de API pela aplicação e devem ser reavaliadas separadamente ao atualizar dependências.

## Alvos de Refatoração MVC

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|
| composição/inicialização | `src/app.js`, construtor/init de `AppManager` | app factory + server/composition root | separar construção da aplicação do processo que abre porta e permitir testes |
| configuração | `src/utils.js:1-7` | `config/` | retirar segredos do código e validar ambiente |
| models/repositories | SQL em `src/AppManager.js` | `models/` e `repositories/` | isolar schema, consultas e transações |
| checkout | `src/AppManager.js:28-78` | route/view + controller + service | separar HTTP da regra e da persistência |
| relatório financeiro | `src/AppManager.js:80-129` | controller + reporting service/repository | eliminar N+1 e proteger acesso |
| usuários | `src/AppManager.js:131-137` | controller + service/repository | garantir autorização e integridade na exclusão |
| segurança transversal | ausente e logs em `AppManager` | `middlewares/` + logger adapter | autenticar, autorizar, tratar erros e redigir dados |
| utilitários | `src/utils.js` | adapters/services específicos | remover estado global e hashing inseguro |

## Plano de Validação para a Fase 3

- Comando de inicialização: `npm start`.
- Endpoints de testes de fumaça: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`.
- Comando de testes: não encontrado; será necessário criar testes de contrato/regressão ou executar fumaça com os exemplos de `api.http`.
- Preparação de dados: banco SQLite em memória, schema e seeds automáticos no boot; preservar dados iniciais observáveis.
- Limitação atual: o executável `node` não está disponível no ambiente desta sessão, portanto a execução dependerá da disponibilização do runtime.
- Arquivo de estado: `reports/.refactor-arch/STATE.md`.

## Pré-condições da Fase 3

- O humano revisou este relatório.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints foi registrado em `STATE.md`.
- A refatoração deve avançar tarefa por tarefa usando `refactor-plan.md` e `refactor-tasks.md`.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
