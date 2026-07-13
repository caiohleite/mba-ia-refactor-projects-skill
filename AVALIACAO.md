# Avaliação da entrega — Skill `refactor-arch`

**Data da avaliação:** 12/07/2026  
**Branch/commit avaliados:** `refactor/refatora-002` / `607ab1e`  
**Resultado:** **APROVADA COM RESSALVAS**  
**Nota final:** **8,6 / 10,0**

## 1. Parecer executivo

A entrega é substancialmente superior à média. Todos os critérios de aceite obrigatórios foram atingidos nos três projetos: a Fase 1 detectou corretamente stack e domínio; a Fase 2 produziu mais de cinco achados, incluindo severidade `CRITICAL` ou `HIGH`; e a Fase 3 resultou em aplicações que iniciam e cujos contratos HTTP principais continuam respondendo. A refatoração não é apenas cosmética: existem separações reais entre routes/views, controllers, services, repositories, configuração e tratamento de erros.

A skill também é muito bem construída. Há um `SKILL.md` claro, três fases sequenciais, barreira de confirmação humana, catálogo com 15 antipadrões, detecção de APIs obsoletas, playbook com dez transformações antes/depois, guidelines MVC, template de relatório, checklist de validação e controle explícito de estado. As cópias presentes nos três projetos são byte a byte idênticas.

Entretanto, a entrega não alcança excelência plena porque algumas conclusões documentais são mais fortes que a evidência técnica. Testes adversariais encontraram falha de concorrência no checkout Node.js, autorização horizontal insuficiente e validações incompletas no Task Manager. Também existem inconsistências entre achados declarados como integralmente corrigidos e o código final, além de problemas de rastreabilidade depois que os artefatos foram movidos para pastas de iteração. Por fim, o documento final está em `README_ENTREGAVEL.md`, enquanto o `README.md` raiz continua contendo o enunciado da atividade.

Em síntese: trata-se de uma entrega tecnicamente forte, bem documentada e plenamente aprovável, mas ainda não suficientemente precisa e robusta para nota máxima.

## 2. Método e rubrica adotados

Como o enunciado define critérios de aceite, mas não atribui pesos, foi aplicada a seguinte rubrica:

| Dimensão | Peso | Nota obtida | Fundamentação resumida |
|---|---:|---:|---|
| Análise manual dos três projetos | 1,5 | **1,40** | Cobertura e justificativas excelentes; há uma inconsistência de rastreio no caso das credenciais de seed do Task Manager. |
| Construção e qualidade da skill | 2,5 | **2,40** | Estrutura completa, reutilizável, segura e compatível com Codex; pequenas oportunidades de maior determinismo e rastreabilidade. |
| Execução, auditorias e evidências | 2,0 | **1,70** | Relatórios fortes e histórico prova a pausa entre fases; alguns caminhos de estado ficaram inválidos e há verificações declaradas como `PASS` sem correspondência exata. |
| Qualidade das refatorações e validação | 3,0 | **2,35** | MVC real e testes aprovados; falhas adversariais de concorrência, autorização e validação impedem pontuação de excelência. |
| README, empacotamento e reprodutibilidade | 1,0 | **0,75** | Conteúdo excepcionalmente completo, porém entregue no nome incorreto e com alegações absolutas que precisam ser moderadas. |
| **Total** | **10,0** | **8,60** | **Aprovada com ressalvas.** |

A avaliação incluiu leitura do enunciado, documentação final, código atual, histórico Git, relatórios das duas iterações, arquivos de estado, planos, tarefas, testes e configurações do Codex. Também foram feitos testes regulares e adversariais, inspeções estáticas e comparação dos relatórios com os commits legados aos quais os findings se referem.

## 3. Conformidade com os critérios de aceite

| Critério obrigatório | Projeto 1 | Projeto 2 | Projeto 3 | Parecer |
|---|---:|---:|---:|---|
| Fase 1 detecta stack corretamente | Atendido | Atendido | Atendido | **3/3** |
| Fase 2 encontra pelo menos 5 findings | 14 | 13 | 13 | **3/3** |
| Fase 2 inclui `CRITICAL` ou `HIGH` | Sim | Sim | Sim | **3/3** |
| Aplicação funciona após a Fase 3 | Sim | Sim | Sim | **3/3** |
| Relatório canônico em `reports/audit-project-N.md` | Sim | Sim | Sim | **3/3** |
| Skill completa dentro dos três projetos | Sim | Sim | Sim | **3/3** |

Os três relatórios canônicos existem na raiz `reports/` com os nomes exatos exigidos. Eles são cópias byte a byte das auditorias iniciais arquivadas nas pastas de cada projeto.

## 4. Análise manual

### Pontos fortes

O `README_ENTREGAVEL.md` documenta 9 problemas no `code-smells-project`, 7 no `ecommerce-api-legacy` e 9 no `task-manager-api`. Todos cumprem a distribuição mínima de severidade. As justificativas não são genéricas: relacionam os sinais encontrados a confidencialidade, integridade, testabilidade, acoplamento, custo de manutenção e desempenho.

A análise demonstra boa compreensão de que organização física não equivale a separação arquitetural. Isso é particularmente bem explorado no Task Manager, cuja estrutura legada já possuía `models/`, `routes/` e `services/`, mas mantinha ORM, transações, regras e serialização nas rotas.

Os achados manuais também serviram efetivamente como baseline para as auditorias. Nos três projetos há mais de cinco correspondências materiais entre problemas manuais e findings automatizados.

### Ressalva

O documento classifica como `CRITICAL` a existência de credenciais demonstrativas fixas no `task-manager-api/seed.py`. Contudo, a auditoria inicial automatizada não criou um finding específico para esse problema e o código final ainda cria `admin` com senha conhecida (`1234`), além de duas outras contas com senhas de quatro caracteres. A reauditoria registra isso apenas dentro do finding `MEDIUM` sobre política de senha.

Isso não invalida o mínimo de cobertura, mas contradiz a afirmação de que a análise manual foi coberta integralmente e de que nenhum risco grave conhecido permanece. Sob a própria régua definida pelo aluno, o problema não foi eliminado; foi contextualizado como credencial de demonstração. O texto deveria assumir explicitamente a reclassificação ou tornar o seed configurável e bloqueado fora de ambiente local.

## 5. Construção da skill

### Conformidade técnica com OpenAI Codex

A adaptação para Codex está correta. A [documentação oficial de skills do Codex](https://developers.openai.com/codex/skills) confirma a descoberta de skills de repositório em `.agents/skills`, o uso de `SKILL.md` com `name` e `description`, referências Markdown, metadados opcionais em `agents/openai.yaml` e invocação explícita por `$nome-da-skill`. A [documentação de subagentes do Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) também confirma agentes de projeto em `.codex/agents/*.toml` com `name`, `description` e `developer_instructions`.

Portanto, não há desconto pela substituição do exemplo `.claude/skills/` por `.agents/skills/`. Trata-se de adaptação legítima à ferramenta escolhida.

### Qualidades do `SKILL.md`

- As três fases são explícitas, sequenciais e possuem entradas e saídas claras.
- A regra de não editar código antes da confirmação aparece no fluxo principal, nas regras de segurança, no estado e nos perfis especializados.
- A Fase 1 exige inventário, detecção por evidências e leitura das responsabilidades reais.
- A Fase 2 exige findings ordenados, arquivo/linha, confiança, impacto, recomendação e verificação de APIs deprecated.
- A Fase 3 exige matriz de cobertura, plano, tarefas pequenas, validação local, boot, endpoints e relatório final.
- O mecanismo `STATE.md` permite retomada e registra permissão para modificação.
- O design usa divulgação progressiva: o orquestrador permanece relativamente conciso e transfere conhecimento extenso para `references/`.

### Arquivos de referência

As cinco áreas obrigatórias estão plenamente cobertas:

1. `project-analysis.md`: linguagem, framework, banco, domínio e arquitetura;
2. `anti-pattern-catalog.md`: 15 antipadrões distribuídos entre as quatro severidades;
3. `audit-report-template.md`: estrutura padronizada da auditoria;
4. `mvc-guidelines.md`: responsabilidades, dependências e variações por stack;
5. `refactoring-playbook.md`: dez transformações com antes/depois.

Além do mínimo, foram incluídos checklist de validação, estado do workflow e sete perfis especializados. Essa extensão é útil e coerente com o risco de uma refatoração ampla.

### Oportunidades de melhoria

- O playbook poderia exigir testes adversariais por categoria de achado, e não apenas validação nominal de boot/endpoints. Transações deveriam implicar rollback induzido e concorrência; autorização deveria implicar testes horizontais e verticais; validação deveria implicar tipos inválidos e estruturas aninhadas.
- Alguns relatórios do projeto Node usam nomes de padrões como `Repository + Unit of Work` ou `Authentication/Authorization Middleware`, enquanto o playbook canônico usa outros títulos. O conteúdo é compatível, mas a matriz de rastreio deveria usar identificadores estáveis de transformação.
- Os agentes de análise usam `sandbox_mode = "workspace-write"` porque precisam produzir relatórios. Isso é funcional, mas seria melhor explicitar no próprio TOML que a escrita é limitada a `reports/`, já que a descrição os chama de “somente leitura”.

## 6. Execução da skill e qualidade dos relatórios

### Evidências fortes

O histórico Git comprova a separação entre auditoria e refatoração. Há commits distintos para cópia da skill, Fases 1/2 e Fase 3 em cada projeto. Isso é uma evidência mais forte que um simples checkbox de que a barreira humana foi respeitada.

Os relatórios iniciais têm findings ordenados, severidades coerentes, localização, evidência, impacto e recomendação. As referências de linha dos arquivos legados foram conferidas contra os commits anteriores à refatoração e são materialmente corretas.

As contagens também são consistentes:

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total inicial |
|---|---:|---:|---:|---:|---:|
| `code-smells-project` | 5 | 4 | 3 | 2 | 14 |
| `ecommerce-api-legacy` | 4 | 3 | 4 | 2 | 13 |
| `task-manager-api` | 4 | 3 | 4 | 2 | 13 |

As reauditorias são uma iniciativa meritória. Elas demonstram que a skill não parou após criar diretórios MVC e voltou a inspecionar o fluxo real.

### Problemas de rastreabilidade

Os artefatos foram posteriormente arquivados em `reports/iteracao-*`, mas diversos caminhos internos continuam apontando para a localização antiga. Exemplos:

- os relatórios canônicos apontam para `reports/.refactor-arch/STATE.md`, que não existe na raiz;
- os `STATE.md` arquivados ainda listam caminhos anteriores à movimentação;
- a iteração 2 arquivada como `iteracao-02-nao_executada` ainda registra caminhos sem esse sufixo.

Isso não afeta a leitura humana dos relatórios, mas quebra a promessa de retomada automática baseada no estado. A solução correta seria manter uma cópia operacional em `reports/.refactor-arch/`, atualizar os links após o arquivamento ou registrar no estado o caminho definitivo.

Também faltou registrar explicitamente o SHA da base auditada. Como os arquivos citados foram removidos na Fase 3, a precisão das linhas depende hoje do histórico Git. Incluir `audited_commit` no relatório e no `STATE.md` tornaria a evidência autocontida.

### Exatidão das validações declaradas

No Task Manager, o relatório da iteração 1 declara `git diff --check` como `PASS`. A repetição contra o commit da Fase 3 (`6612602^..6612602`) retorna código 2 e quinze ocorrências de `new blank line at EOF`. O defeito é cosmético, mas a evidência factual está incorreta.

No projeto 1, a comparação da primeira Fase 3 também encontra whitespace no próprio relatório de validação, embora a segunda iteração esteja limpa. Novamente, o impacto no produto é mínimo; o problema é a precisão de uma afirmação de verificação.

## 7. Avaliação das refatorações

### 7.1 `code-smells-project`

Este é o resultado mais sólido dos três. O projeto saiu de quatro módulos fortemente acoplados para uma arquitetura coerente com application factory, views/Blueprints, controllers, services, repositories, models/DTOs, configuração, autenticação e erros centralizados.

Foram corrigidos de forma convincente:

- SQL livre e consultas inseguras;
- exposição de senha/hash e segredo no health check;
- senha em texto puro, com migração de registros legados no login;
- conexão SQLite global;
- N+1 na montagem de pedidos;
- falta de atomicidade no pedido e inconsistência de estoque no cancelamento;
- endpoints administrativos fail-open;
- ausência de autenticação, papel e ownership;
- DDL/seed automático no boot padrão;
- constraints e soft delete.

A suíte independente foi reproduzida com **11 testes aprovados**. Os testes verificam contratos exatos, autorização, segurança dos DTOs, sanitização de erros, constraints, migração, estoque, descontos e endpoints administrativos. Não foi encontrada regressão funcional relevante no estado final.

Ressalvas remanescentes são principalmente operacionais e estão documentadas: segredo estável em produção, HTTPS/cookies seguros, CORS e servidor WSGI. Essas limitações não retiram o mérito da refatoração.

**Avaliação parcial do projeto:** excelente, aproximadamente **9,3/10**.

### 7.2 `ecommerce-api-legacy`

A decomposição do `AppManager` é tecnicamente boa. Routes, controllers, services, repositories, middlewares, erros, configuração e composition root possuem responsabilidades reconhecíveis. O projeto preserva CommonJS, em vez de impor uma migração tecnológica desnecessária. Também há melhorias reais em senha (`scrypt` com salt), proteção administrativa fail-closed, SQL parametrizado, JOIN para relatório, foreign keys, cascata e rollback sequencial.

`npm test` foi reproduzido com sucesso. A primeira tentativa no sandbox falhou apenas porque o ambiente não permitia abrir socket; fora dessa restrição, a suíte apresentou:

```text
PASS: regressão funcional, segurança e arquitetura MVC
```

#### Falha relevante: concorrência transacional

`server.js` compartilha uma única conexão SQLite entre todos os requests e `TransactionManager` executa `BEGIN IMMEDIATE` nessa conexão sem fila ou mutex. Em um teste adversarial com três checkouts simultâneos, apenas um concluiu; dois falharam com:

```text
SQLITE_ERROR: cannot start a transaction within a transaction
```

Logo, a atomicidade sequencial está correta, mas a fronteira transacional não funciona sob concorrência normal. Isso contradiz a formulação ampla de que as transações foram integralmente validadas. A correção exige serialização por conexão ou conexões independentes/pool, acompanhada de teste concorrente.

#### Segurança de dependências

Em 12/07/2026, `npm audit --omit=dev --audit-level=moderate` reportou **13 vulnerabilidades: 2 low, 5 moderate e 6 high** no lockfile atual. Parte dos achados está em dependências de instalação do ramo `sqlite3/node-gyp` e precisa de triagem de explorabilidade; não é correto tratá-los automaticamente como seis vulnerabilidades de runtime. Ainda assim, a reauditoria que afirma zero `HIGH` conhecido é incompleta por não registrar essa verificação.

O próprio `node-sqlite3` está deprecated/unmaintained, fato corretamente encontrado na segunda auditoria. A substituição deve considerar a versão mínima do Node e não ser feita mecanicamente.

#### Outras ressalvas

- O finding original sobre endpoint destrutivo recomendava também auditoria da operação, mas a exclusão de usuário não grava evento de auditoria.
- `startServer()` retorna antes de confirmar o evento `listening` e não trata o evento de erro do servidor; a segunda auditoria reconhece corretamente o problema.
- A suíte não cobre concorrência, idempotência, falha de bind nem rollback induzido após uma escrita intermediária. Um ensaio independente de falha no `AuditRepository` confirmou que o rollback sequencial funciona, o que é positivo.

**Avaliação parcial do projeto:** boa/muito boa, aproximadamente **8,2/10**.

### 7.3 `task-manager-api`

A refatoração arquitetural é materialmente boa. As rotas foram reduzidas a Blueprints/decorators; controllers adaptam HTTP; services coordenam regras e transações; repositories encapsulam SQLAlchemy, eager loading e agregações; schemas centralizam DTOs e parte das validações; middlewares centralizam autenticação e erros.

A suíte foi reproduzida com **4 testes aprovados**, e esses testes exercitam as 22 combinações método/caminho. O boot e o seed in-memory também são reproduzíveis. Houve melhorias significativas: senha forte para novos registros, token assinado e expirável, DTO sem hash, papéis administrativos, remoção de ORM das rotas/controllers e eliminação de N+1 no fluxo principal.

#### Falha relevante: autorização horizontal de tarefas

As mutações de tarefas exigem apenas que exista algum usuário autenticado. O controller não passa o ator ao service, e `TaskService` não verifica proprietário nem papel. Em teste adversarial, um usuário comum conseguiu atualizar e excluir a tarefa de outro usuário, recebendo HTTP 200.

Além disso, os endpoints de leitura de tarefas continuam anônimos e expõem descrição, responsável e categoria. A segunda auditoria registra a leitura pública como `MEDIUM`, mas não identifica a autorização horizontal das mutações. Isso significa que o finding original sobre proteção de operações foi mitigado, não integralmente eliminado.

#### Falha relevante: payload inválido vira HTTP 500

`validate_task_payload()` não valida os tipos de `description`, `user_id` e `category_id`; `validate_category_payload()` não valida o tipo de `description`. Payloads com objetos JSON nesses campos chegam ao ORM e produzem erro interno sanitizado, com HTTP 500, em vez de erro de entrada 400.

Foram reproduzidos, entre outros:

- criação de tarefa com `description` como objeto: **500**;
- criação de tarefa com `user_id` como objeto: **500**;
- criação de categoria com `description` como objeto: **500**.

O tratamento central evita vazamento de detalhes, mas a classificação HTTP está errada e a alegação de validação completa é excessiva.

#### Demais ressalvas

- O seed ainda cria um administrador com senha conhecida e curta, apesar de a análise manual ter classificado credenciais de seed como `CRITICAL`.
- `create_all()` continua dentro da factory e o módulo instancia a aplicação no import, produzindo efeitos persistentes implícitos.
- A ponte MD5 continua ativa até o login de registros legados; a estratégia é defensável como migração temporária, mas precisa de prazo de remoção.
- `utils/helpers.py` e `NotificationService` permanecem sem consumidores, embora AP-15 tenha sido marcado como `FIXED` na primeira validação. A reauditoria reconhece posteriormente o resíduo.
- A política mínima de quatro caracteres é inadequada para um produto real.

**Avaliação parcial do projeto:** boa/muito boa, aproximadamente **8,5/10**.

## 8. Qualidade do README e do empacotamento

### Conteúdo

O conteúdo de `README_ENTREGAVEL.md` é excelente em abrangência. Ele contém todas as seções A–D exigidas:

- análise manual por projeto, severidade e justificativa;
- decisões de design e catálogo;
- explicação da neutralidade tecnológica;
- desafios e soluções;
- contagens por severidade;
- estruturas antes/depois;
- checklists preenchidos;
- logs de testes e boots;
- comparação entre stacks;
- pré-requisitos, invocação e validação.

Os links locais foram verificados e resolvem corretamente. A documentação dos projetos também é útil, especialmente nas variáveis de ambiente, autenticação, endpoints e riscos operacionais.

### Não conformidade formal

O enunciado exige `README.md` atualizado, mas o `README.md` raiz continua sendo o enunciado e o texto final está em `README_ENTREGAVEL.md`. Isso prejudica a apresentação no GitHub e constitui não conformidade objetiva do entregável, ainda que o conteúdo solicitado exista.

Há ainda um risco de publicação: o trabalho está na branch `refactor/refatora-002`, enquanto `origin/HEAD` aponta para `origin/main`, que permanece no boilerplate inicial. Para uma entrega pública, deve-se fazer merge para a branch padrão ou configurar explicitamente a branch entregue como default.

### Precisão da narrativa

Formulações como “todos os achados corrigidos”, “nenhum `CRITICAL` ou `HIGH` conhecido” e “autorização/transações validadas” devem ser substituídas por afirmações limitadas ao que foi efetivamente testado. A documentação é transparente ao listar vários riscos residuais, mas contradiz essa transparência quando usa conclusões absolutas no resumo executivo.

## 9. Evidências reproduzidas

| Verificação | Resultado |
|---|---|
| `code-smells-project`: `python3 -m unittest discover -v` | **11/11 PASS** |
| `ecommerce-api-legacy`: `npm test` | **PASS** |
| `task-manager-api`: `DATABASE_URL=sqlite:///:memory: python3 -m unittest discover -s tests -v` | **4/4 PASS** |
| Comparação das três cópias da skill | **Sem diferenças** |
| Links locais do `README_ENTREGAVEL.md` | **Sem links quebrados** |
| Relatórios canônicos `reports/audit-project-{1,2,3}.md` | **Presentes e versionados** |
| Checkout Node concorrente, 3 operações | **1 sucesso; 2 falhas transacionais** |
| Mutação de tarefa alheia por usuário comum | **Permitida indevidamente (200)** |
| Payloads estruturais inválidos no Task Manager | **500 em casos que deveriam retornar 400** |
| `git diff --check 6612602^ 6612602 -- task-manager-api` | **Falha, apesar do relatório declarar PASS** |
| `npm audit --omit=dev --audit-level=moderate` em 12/07/2026 | **13 alertas; triagem necessária** |

A primeira execução local do projeto 1 foi tentada com o `venv/` ali existente e falhou porque esse ambiente contém `pip`, mas não Flask. O comando documentado com o Python do ambiente funcional passou. O `venv/` local é ignorado pelo Git e não compõe a entrega versionada; portanto, isso não foi tratado como defeito do código, mas reforça a necessidade de criar o ambiente e instalar `requirements.txt` antes dos testes.

## 10. Prioridades para elevar a entrega a nível de excelência

### Prioridade 1 — corrigir defeitos funcionais e de segurança

1. Serializar transações na conexão SQLite do projeto Node ou usar conexões independentes; adicionar teste de checkout concorrente.
2. Implementar autorização por proprietário/papel em `PUT` e `DELETE /tasks/<id>` e decidir/documentar se leituras de tarefa são públicas.
3. Completar validação de tipos no Task Manager para que payloads inválidos retornem 400.
4. Remover credenciais conhecidas do seed ou exigir configuração explícita, bloqueando seed demonstrativo fora de ambiente local.
5. Triar e atualizar as dependências sinalizadas pelo `npm audit` sem quebrar a compatibilidade do projeto.

### Prioridade 2 — tornar as evidências incontestáveis

1. Incorporar testes adversariais de concorrência, rollback induzido, autorização horizontal, tipos inválidos, bind e idempotência.
2. Registrar o commit auditado em todos os relatórios.
3. Atualizar caminhos do `STATE.md` depois de arquivar iterações.
4. Fazer as verificações falharem quando o comando real falhar; não registrar `PASS` a partir de uma inferência ou de uma execução sobre escopo diferente.
5. Distinguir `FIX`, `PARTIAL` e `DEFER` com maior rigor. Um item não deve ser `FIXED` se parte relevante da recomendação ou do risco permanece.

### Prioridade 3 — corrigir a apresentação formal

1. Substituir o `README.md` raiz pelo conteúdo de `README_ENTREGAVEL.md`.
2. Fazer merge da entrega na branch padrão do repositório ou alterar a branch default.
3. Revisar os resumos para remover afirmações absolutas incompatíveis com o backlog e os testes adversariais.
4. Manter os relatórios canônicos e, adicionalmente, links válidos para os artefatos completos de cada iteração.

## 11. Justificativa final da nota

A nota **8,6/10** reconhece uma entrega madura, extensa e tecnicamente competente. A skill supera com folga os mínimos de conteúdo, funciona nos três projetos-alvo, impõe aprovação humana antes da alteração, produz auditorias úteis e conduziu refatorações MVC reais. O histórico, os relatórios e as suítes fornecem evidência substancial de autoria e execução.

O desconto de 1,4 ponto não decorre de preferências estilísticas. Ele decorre de defeitos reproduzíveis e relevantes: concorrência transacional quebrada no checkout, autorização horizontal insuficiente, validações que geram 500, dívida de dependências não capturada, inconsistências em resultados declarados como `PASS`, achados marcados como integralmente corrigidos apesar de resíduos e uma entrega documental fora do nome/branch esperados.

Com as correções prioritárias acima, a solução teria condições de alcançar a faixa **9,5–10,0**. No estado avaliado, **8,6** é uma nota exigente, imparcial e proporcional: premia a excelente arquitetura e documentação, mas não confunde atendimento ao mínimo com ausência de falhas.
