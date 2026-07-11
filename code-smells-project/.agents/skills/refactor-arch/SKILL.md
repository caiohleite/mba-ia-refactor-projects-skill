---
name: refactor-arch
description: Analisa, audita e refatora codebases legadas de backend para o padrão MVC, de forma agnóstica de tecnologia. Use quando Codex precisar detectar stack e arquitetura atual, identificar anti-patterns e code smells com severidade e linhas exatas, gerar relatório de auditoria, pausar para confirmação humana, reestruturar para Model-View-Controller e validar boot/endpoints após as mudanças em projetos Python/Flask, Node.js/Express ou stacks similares.
---

# Refactor Arch

Use esta skill para executar um fluxo completo de modernização arquitetural orientado a MVC. A execução possui três fases sequenciais e obrigatórias:

1. **Análise**: detectar linguagem, framework, banco de dados, domínio, arquivos relevantes e arquitetura atual.
2. **Auditoria**: cruzar o código contra o catálogo de anti-patterns, classificar severidade, gerar relatório e pedir confirmação.
3. **Refatoração**: somente após confirmação, reorganizar o projeto para MVC e validar que a aplicação continua funcionando.

## Recursos

Leia apenas os recursos necessários para a fase atual:

- `references/project-analysis.md`: heurísticas da Fase 1 para detectar stack, domínio, banco de dados e arquitetura.
- `references/anti-pattern-catalog.md`: catálogo da Fase 2 com severidades, sinais de detecção e recomendações.
- `references/audit-report-template.md`: formato obrigatório do relatório de auditoria.
- `references/mvc-guidelines.md`: arquitetura MVC alvo, responsabilidades por camada e variações por stack.
- `references/refactoring-playbook.md`: transformações concretas com exemplos antes/depois.
- `references/validation-checklist.md`: validação de boot, endpoints, testes e regressão arquitetural.
- `references/workflow-state.md`: artefatos de estado, checkpoints, retomada e controle de tarefas.
- `references/agents/*.md`: perfis especializados dos agentes da skill.

## Agentes

Cada objetivo principal da skill possui um agente dedicado. Antes de executar uma fase no agente principal ou delegar para subagentes, leia o perfil correspondente:

| Objetivo | Perfil | Agente customizado |
|---|---|---|
| Analisar codebase e arquitetura atual | `references/agents/project-analyzer.md` | `refactor-project-analyzer` |
| Identificar anti-patterns e code smells | `references/agents/anti-pattern-auditor.md` | `refactor-anti-pattern-auditor` |
| Gerar relatório estruturado e pedido de confirmação | `references/agents/audit-reporter.md` | `refactor-audit-reporter` |
| Planejar refatoração MVC | `references/agents/refactoring-planner.md` | `refactor-planner` |
| Quebrar plano em tarefas executáveis | `references/agents/refactoring-task-writer.md` | `refactor-task-writer` |
| Implementar mudanças passo a passo | `references/agents/mvc-refactor-implementer.md` | `refactor-mvc-implementer` |
| Validar resultado final | `references/agents/refactoring-validator.md` | `refactor-validator` |

Use subagentes quando a sessão atual permitir e o pedido do usuário incluir execução com agentes/subagentes. Caso contrário, execute as responsabilidades no agente principal seguindo os mesmos perfis. Em todos os casos, mantenha uma única linha de decisão no agente principal: nenhuma modificação antes da confirmação ao fim da Fase 2.

## Entradas

Extraia estes parâmetros do pedido do usuário:

- `project-folder`: escopo da análise. Padrão: diretório atual.
- `reports-folder`: destino do relatório. Padrão: `reports` relativo ao repositório ou ao projeto.
- `report-name`: nome do relatório de auditoria. Padrão: `audit-[nome-do-projeto].md`; nos projetos do desafio, usar `audit-project-1.md`, `audit-project-2.md` ou `audit-project-3.md` quando o projeto for reconhecido.
- `ignore-folders`: pastas e arquivos a ignorar. Sempre incluir `.git`, dependências vendorizadas, caches e artefatos gerados.
- `validation-base-url`: URL local para smoke tests, quando informada.

Se o escopo não tiver código-fonte detectável, peça o caminho correto antes de prosseguir.

## Controle de Estado

Leia `references/workflow-state.md` antes de iniciar a Fase 1 ou retomar uma execução existente.

- Crie e mantenha `reports-folder/.refactor-arch/STATE.md` como fonte de verdade do fluxo de trabalho.
- Antes da confirmação da Fase 2, somente artefatos de fluxo de trabalho e relatórios podem ser criados ou atualizados; não edite código-fonte, manifests, lockfiles, configuração da aplicação ou banco.
- Atualize `STATE.md` ao iniciar e concluir cada fase, antes e depois de cada tarefa da Fase 3, e sempre que houver erro, bloqueio ou decisão humana.
- Registre contratos de endpoints detectados, caminhos de artefatos, achados por severidade, status das tarefas, comandos de validação e próximo passo.
- Ao retomar, leia `STATE.md` primeiro e continue da primeira fase ou tarefa `PENDING` ou `FAILED`.

## Regras de Segurança

- Não altere código-fonte, manifests, lockfiles, configuração da aplicação ou banco antes de concluir a Fase 2 e receber confirmação explícita do usuário; antes disso, crie ou atualize somente artefatos de fluxo de trabalho e relatórios.
- Antes de editar, verifique o estado do worktree e preserve mudanças preexistentes.
- Mantenha endpoints, contratos HTTP, comandos de boot e comportamento observável, salvo quando o relatório e a confirmação aprovarem mudança específica.
- Nunca invente achados. Cada achado deve citar arquivo e linha exatos ou declarar que a evidência é estrutural e explicar como foi inferida.
- Não remover funcionalidade para facilitar a refatoração.
- Não executar comandos destrutivos. Para limpeza, prefira remover apenas artefatos claramente gerados pela própria validação e peça confirmação quando houver risco.

## Fase 1: Análise

1. Leia `references/project-analysis.md`, `references/workflow-state.md` e `references/agents/project-analyzer.md`.
2. Inventarie arquivos de código, manifests, rotas, schemas, configurações, testes e scripts de execução.
3. Detecte linguagem, framework, banco de dados, domínio da aplicação, padrão arquitetural atual e contagem de arquivos analisados.
4. Mapeie camadas reais, não apenas nomes de pastas. Um projeto com `routes/`, `models/` ou `services/` ainda pode violar MVC.
5. Salve a análise em `reports-folder/.refactor-arch/phase-1-analysis.md` e atualize `STATE.md`.
6. Imprima um resumo no formato:

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:           [linguagem]
Framework:           [framework]
Dependências:        [principais dependências]
Domínio:             [domínio inferido]
Arquitetura:         [arquitetura atual e problemas macro]
Arquivos-fonte:      [N] arquivos analisados
Tabelas do banco:    [tabelas/modelos detectados]
================================
```

## Fase 2: Auditoria

1. Leia `references/anti-pattern-catalog.md`, `references/audit-report-template.md`, `references/workflow-state.md`, `references/agents/anti-pattern-auditor.md` e `references/agents/audit-reporter.md`.
2. Audite o código contra o catálogo, incluindo APIs obsoletas quando aplicável.
3. Classifique achados em `CRITICAL`, `HIGH`, `MEDIUM` e `LOW` usando a escala do catálogo.
4. Inclua pelo menos 5 achados quando houver evidência suficiente; para cada achado, informe arquivo, linha inicial e linha final quando aplicável.
5. Ordene achados por severidade, depois por impacto arquitetural.
6. Salve o relatório em `reports-folder/[report-name]` quando um destino estiver disponível.
7. Atualize `STATE.md` com contagens, caminho do relatório, alvos MVC e `Confirmação humana para a Fase 3: PENDING`.
8. Pause obrigatoriamente:

```text
Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
```

Se a resposta não for afirmativa e explícita, encerre sem modificar o projeto.

## Fase 3: Refatoração

Execute esta fase somente após confirmação.

1. Leia `references/mvc-guidelines.md`, `references/refactoring-playbook.md`, `references/validation-checklist.md`, `references/workflow-state.md` e os perfis `refactoring-planner`, `refactoring-task-writer`, `mvc-refactor-implementer` e `refactoring-validator`.
2. Gere um plano de refatoração baseado nos achados aprovados e na arquitetura alvo. O plano deve conter uma matriz de cobertura ligando cada achado do relatório a uma decisão: `FIX`, `PARTIAL`, `DEFER`, `ACCEPT_RISK` ou `NOT_APPLICABLE`, sempre com justificativa.
3. Salve o plano em `reports-folder/.refactor-arch/refactor-plan.md` e atualize `STATE.md`.
4. Não avance para tarefas enquanto houver achado aprovado sem decisão, sem tarefa associada ou sem justificativa explícita.
5. Quebre o plano em tarefas pequenas, ordenadas por menor risco: configuração, models/repositories, controllers/services, routes/views, middlewares, bootstrap e validação.
6. Cada tarefa deve apontar quais etapas do plano e quais achados cobre, quais arquivos provavelmente altera, quais referências usar, critério de aceite e validação local.
7. Salve as tarefas em `reports-folder/.refactor-arch/refactor-tasks.md` e espelhe seus status no `STATE.md`.
8. Implemente uma tarefa por vez, marcando `IN_PROGRESS` antes de editar e `COMPLETED`, `FAILED` ou `SKIPPED` após validar.
9. Verifique imports, caminhos, inicialização, contrato dos endpoints originais e compatibilidade dos payloads/respostas.
10. Extraia configuração sensível para variáveis de ambiente ou módulo de configuração com defaults seguros para desenvolvimento.
11. Separe responsabilidades:
   - Models representam dados, schemas e persistência.
   - Views/Routes expõem HTTP e serialização.
   - Controllers coordenam fluxo de caso de uso.
   - Services concentram regras de negócio quando o domínio exigir.
   - Middlewares tratam erros, auth, logging e concerns transversais.
12. Valide boot da aplicação, endpoints originais, redução dos anti-patterns encontrados e cobertura final de todos os achados.
13. Salve `reports-folder/.refactor-arch/validation-report.md` e atualize `STATE.md`.
14. Gere um resumo final com nova estrutura, comandos executados e limitações.

## Recuperação

Se o fluxo for interrompido:

1. Leia `reports-folder/.refactor-arch/STATE.md` antes de qualquer outra ação.
2. Verifique se os artefatos registrados no estado existem.
3. Confira o diff/worktree atual antes de decidir a próxima tarefa.
4. Retome da primeira fase ou tarefa `PENDING` ou `FAILED`.
5. Não reexecute tarefas `COMPLETED` sem pedido explícito do usuário.
6. Se `Modificações no código-fonte permitidas` estiver `NO`, não edite código.
7. Se a confirmação da Fase 2 não estiver registrada em `STATE.md` e na conversa atual, volte a pedir confirmação antes de editar.

## Saída Final

Ao concluir, informe:

- caminho do relatório de auditoria;
- arquivos principais criados ou alterados;
- nova estrutura MVC;
- validações executadas e resultado;
- riscos restantes ou comandos que não puderam ser executados.
