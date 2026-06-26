---
name: refactor-arch
description: Analisa, audita e refatora codebases legadas de backend para o padrao MVC, de forma agnostica de tecnologia. Use quando Codex precisar detectar stack e arquitetura atual, identificar anti-patterns e code smells com severidade e linhas exatas, gerar relatorio de auditoria, pausar para confirmacao humana, reestruturar para Model-View-Controller e validar boot/endpoints apos as mudancas em projetos Python/Flask, Node.js/Express ou stacks similares.
---

# Refactor Arch

Use esta skill para executar um fluxo completo de modernizacao arquitetural orientado a MVC. A execucao possui tres fases sequenciais e obrigatorias:

1. **Analise**: detectar linguagem, framework, banco de dados, dominio, arquivos relevantes e arquitetura atual.
2. **Auditoria**: cruzar o codigo contra o catalogo de anti-patterns, classificar severidade, gerar relatorio e pedir confirmacao.
3. **Refatoracao**: somente apos confirmacao, reorganizar o projeto para MVC e validar que a aplicacao continua funcionando.

## Recursos

Leia apenas os recursos necessarios para a fase atual:

- `references/project-analysis.md`: heuristicas da Fase 1 para detectar stack, dominio, banco de dados e arquitetura.
- `references/anti-pattern-catalog.md`: catalogo da Fase 2 com severidades, sinais de deteccao e recomendacoes.
- `references/audit-report-template.md`: formato obrigatorio do relatorio de auditoria.
- `references/mvc-guidelines.md`: arquitetura MVC alvo, responsabilidades por camada e variacoes por stack.
- `references/refactoring-playbook.md`: transformacoes concretas com exemplos antes/depois.
- `references/validation-checklist.md`: validacao de boot, endpoints, testes e regressao arquitetural.
- `references/workflow-state.md`: artefatos de estado, checkpoints, retomada e controle de tarefas.
- `references/agents/*.md`: perfis especializados dos agentes da skill.

## Agentes

Cada objetivo principal da skill possui um agente dedicado. Antes de executar uma fase no agente principal ou delegar para subagentes, leia o perfil correspondente:

| Objetivo | Perfil | Agente customizado |
|---|---|---|
| Analisar codebase e arquitetura atual | `references/agents/project-analyzer.md` | `refactor-project-analyzer` |
| Identificar anti-patterns e code smells | `references/agents/anti-pattern-auditor.md` | `refactor-anti-pattern-auditor` |
| Gerar relatorio estruturado e pedido de confirmacao | `references/agents/audit-reporter.md` | `refactor-audit-reporter` |
| Planejar refatoracao MVC | `references/agents/refactoring-planner.md` | `refactor-planner` |
| Quebrar plano em tarefas executaveis | `references/agents/refactoring-task-writer.md` | `refactor-task-writer` |
| Implementar mudancas passo a passo | `references/agents/mvc-refactor-implementer.md` | `refactor-mvc-implementer` |
| Validar resultado final | `references/agents/refactoring-validator.md` | `refactor-validator` |

Use subagentes quando a sessao atual permitir e o pedido do usuario incluir execucao com agentes/subagentes. Caso contrario, execute as responsabilidades no agente principal seguindo os mesmos perfis. Em todos os casos, mantenha uma unica linha de decisao no agente principal: nenhuma modificacao antes da confirmacao ao fim da Fase 2.

## Entradas

Extraia estes parametros do pedido do usuario:

- `project-folder`: escopo da analise. Padrao: diretorio atual.
- `reports-folder`: destino do relatorio. Padrao: `reports` relativo ao repositorio ou ao projeto.
- `report-name`: nome do relatorio de auditoria. Padrao: `audit-[project-name].md`; nos projetos do desafio, usar `audit-project-1.md`, `audit-project-2.md` ou `audit-project-3.md` quando o projeto for reconhecido.
- `ignore-folders`: pastas e arquivos a ignorar. Sempre incluir `.git`, dependencias vendorizadas, caches e artefatos gerados.
- `validation-base-url`: URL local para smoke tests, quando informada.

Se o escopo nao tiver codigo-fonte detectavel, peca o caminho correto antes de prosseguir.

## Controle De Estado

Leia `references/workflow-state.md` antes de iniciar a Fase 1 ou retomar uma execucao existente.

- Crie e mantenha `reports-folder/.refactor-arch/STATE.md` como fonte de verdade do workflow.
- Antes da confirmacao da Fase 2, somente artefatos de workflow e relatorios podem ser criados ou atualizados; nao edite codigo-fonte, manifests, lockfiles, configuracao da aplicacao ou banco.
- Atualize `STATE.md` ao iniciar e concluir cada fase, antes e depois de cada tarefa da Fase 3, e sempre que houver erro, bloqueio ou decisao humana.
- Registre contratos de endpoints detectados, caminhos de artefatos, findings por severidade, status das tarefas, comandos de validacao e proximo passo.
- Ao retomar, leia `STATE.md` primeiro e continue da primeira fase ou tarefa `PENDING` ou `FAILED`.

## Regras De Seguranca

- Nao altere codigo-fonte, manifests, lockfiles, configuracao da aplicacao ou banco antes de concluir a Fase 2 e receber confirmacao explicita do usuario; antes disso, crie ou atualize somente artefatos de workflow e relatorios.
- Antes de editar, verifique o estado do worktree e preserve mudancas preexistentes.
- Mantenha endpoints, contratos HTTP, comandos de boot e comportamento observavel, salvo quando o relatorio e a confirmacao aprovarem mudanca especifica.
- Nunca invente findings. Cada finding deve citar arquivo e linha exatos ou declarar que a evidencia e estrutural e explicar como foi inferida.
- Nao remover funcionalidade para facilitar a refatoracao.
- Nao executar comandos destrutivos. Para limpeza, prefira remover apenas artefatos claramente gerados pela propria validacao e peca confirmacao quando houver risco.

## Fase 1: Analise

1. Leia `references/project-analysis.md`, `references/workflow-state.md` e `references/agents/project-analyzer.md`.
2. Inventarie arquivos de codigo, manifests, rotas, schemas, configuracoes, testes e scripts de execucao.
3. Detecte linguagem, framework, banco de dados, dominio da aplicacao, padrao arquitetural atual e contagem de arquivos analisados.
4. Mapeie camadas reais, nao apenas nomes de pastas. Um projeto com `routes/`, `models/` ou `services/` ainda pode violar MVC.
5. Salve a analise em `reports-folder/.refactor-arch/phase-1-analysis.md` e atualize `STATE.md`.
6. Imprima um resumo no formato:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      [linguagem]
Framework:     [framework]
Dependencies:  [principais dependencias]
Domain:        [dominio inferido]
Architecture:  [arquitetura atual e problemas macro]
Source files:  [N] files analyzed
DB tables:     [tabelas/modelos detectados]
================================
```

## Fase 2: Auditoria

1. Leia `references/anti-pattern-catalog.md`, `references/audit-report-template.md`, `references/workflow-state.md`, `references/agents/anti-pattern-auditor.md` e `references/agents/audit-reporter.md`.
2. Audite o codigo contra o catalogo, incluindo APIs deprecated quando aplicavel.
3. Classifique findings em `CRITICAL`, `HIGH`, `MEDIUM` e `LOW` usando a escala do catalogo.
4. Inclua pelo menos 5 findings quando houver evidencia suficiente; para cada finding, informe arquivo, linha inicial e linha final quando aplicavel.
5. Ordene findings por severidade, depois por impacto arquitetural.
6. Salve o relatorio em `reports-folder/[report-name]` quando um destino estiver disponivel.
7. Atualize `STATE.md` com contagens, caminho do relatorio, alvos MVC e `Human confirmation for Phase 3: PENDING`.
8. Pause obrigatoriamente:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Se a resposta nao for afirmativa e explicita, encerre sem modificar o projeto.

## Fase 3: Refatoracao

Execute esta fase somente apos confirmacao.

1. Leia `references/mvc-guidelines.md`, `references/refactoring-playbook.md`, `references/validation-checklist.md`, `references/workflow-state.md` e os perfis `refactoring-planner`, `refactoring-task-writer`, `mvc-refactor-implementer` e `refactoring-validator`.
2. Gere um plano de refatoracao baseado nos findings aprovados e na arquitetura alvo.
3. Salve o plano em `reports-folder/.refactor-arch/refactor-plan.md` e atualize `STATE.md`.
4. Quebre o plano em tarefas pequenas, ordenadas por menor risco: configuracao, models/repositories, controllers/services, routes/views, middlewares, bootstrap e validacao.
5. Salve as tarefas em `reports-folder/.refactor-arch/refactor-tasks.md` e espelhe seus status no `STATE.md`.
6. Implemente uma tarefa por vez, marcando `IN_PROGRESS` antes de editar e `COMPLETED`, `FAILED` ou `SKIPPED` apos validar.
7. Verifique imports, caminhos, inicializacao, contrato dos endpoints originais e compatibilidade dos payloads/respostas.
8. Extraia configuracao sensivel para variaveis de ambiente ou modulo de configuracao com defaults seguros para desenvolvimento.
9. Separe responsabilidades:
   - Models representam dados, schemas e persistencia.
   - Views/Routes expoem HTTP e serializacao.
   - Controllers coordenam fluxo de caso de uso.
   - Services concentram regras de negocio quando o dominio exigir.
   - Middlewares tratam erros, auth, logging e concerns transversais.
10. Valide boot da aplicacao, endpoints originais e reducao dos anti-patterns encontrados.
11. Salve `reports-folder/.refactor-arch/validation-report.md` e atualize `STATE.md`.
12. Gere um resumo final com nova estrutura, comandos executados e limitacoes.

## Recuperacao

Se o fluxo for interrompido:

1. Leia `reports-folder/.refactor-arch/STATE.md` antes de qualquer outra acao.
2. Verifique se os artefatos registrados no estado existem.
3. Confira o diff/worktree atual antes de decidir a proxima tarefa.
4. Retome da primeira fase ou tarefa `PENDING` ou `FAILED`.
5. Nao reexecute tarefas `COMPLETED` sem pedido explicito do usuario.
6. Se `Source modifications allowed` estiver `NO`, nao edite codigo.
7. Se a confirmacao da Fase 2 nao estiver registrada em `STATE.md` e na conversa atual, volte a pedir confirmacao antes de editar.

## Saida Final

Ao concluir, informe:

- caminho do relatorio de auditoria;
- arquivos principais criados ou alterados;
- nova estrutura MVC;
- validacoes executadas e resultado;
- riscos restantes ou comandos que nao puderam ser executados.
