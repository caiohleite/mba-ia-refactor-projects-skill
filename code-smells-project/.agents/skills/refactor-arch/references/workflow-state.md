# Controle De Estado E Recuperacao

Use este guia em todas as fases da skill `refactor-arch`. O objetivo e permitir retomada precisa apos interrupcao, sem repetir etapas concluidas nem perder controle das tarefas executadas.

## Artefatos Gerados

Crie e mantenha estes artefatos dentro de `reports-folder/.refactor-arch/`:

```text
reports-folder/
|-- audit-[project-name].md
`-- .refactor-arch/
    |-- STATE.md
    |-- phase-1-analysis.md
    |-- refactor-plan.md
    |-- refactor-tasks.md
    `-- validation-report.md
```

Antes da confirmacao da Fase 2, somente estes artefatos de workflow e o relatorio de auditoria podem ser criados ou atualizados. Codigo-fonte, manifests, lockfiles, configuracao da aplicacao e banco de dados nao devem ser alterados antes da confirmacao explicita.

## STATE.md

`STATE.md` e a fonte de verdade para retomada. Atualize-o ao inicio e ao fim de cada fase, antes e depois de cada tarefa de refatoracao, e sempre que uma validacao falhar.

Modelo:

```markdown
# Refactor Arch State - [PROJECT_NAME]

Generated on: [YYYY-MM-DD HH:MM:SS]
Last updated: [YYYY-MM-DD HH:MM:SS]

## Parameters
- Project folder: [path]
- Reports folder: [path]
- Report name: [audit file]
- Ignore folders: [items]
- Validation base URL: [url or not provided]

## Execution Status
- Current phase: [PHASE_1_ANALYSIS|PHASE_2_AUDIT|WAITING_CONFIRMATION|PHASE_3_PLANNING|PHASE_3_TASKS|PHASE_3_IMPLEMENTATION|PHASE_3_VALIDATION|COMPLETED|PARTIAL|BLOCKED]
- Source modifications allowed: [NO|YES]
- Human confirmation for Phase 3: [PENDING|APPROVED|DECLINED]
- Last completed step: [short description]
- Next step: [short description]

## Artifacts
- Phase 1 analysis: [path or PENDING]
- Audit report: [path or PENDING]
- Refactor plan: [path or PENDING]
- Task list: [path or PENDING]
- Validation report: [path or PENDING]

## Findings Summary
- CRITICAL: [N]
- HIGH: [N]
- MEDIUM: [N]
- LOW: [N]

## Refactoring Tasks
| ID | Status | Finding IDs | Files | Validation | Notes |
|---|---|---|---|---|---|
| T01 | PENDING | AP-XX | path | command/check | notes |

## Endpoint Contract
| Method | Path | Purpose | Source | Status |
|---|---|---|---|---|

## Validation Log
| Time | Command/Check | Result | Notes |
|---|---|---|---|

## Errors And Recovery Notes
- [timestamp] [error or decision]
```

## Status Rules

- `PENDING`: ainda nao iniciado.
- `IN_PROGRESS`: em execucao agora.
- `COMPLETED`: concluido e validado.
- `FAILED`: executado com erro; exige correcao ou decisao.
- `SKIPPED`: omitido com justificativa explicita.
- `BLOCKED`: impossivel avancar sem entrada humana ou dependencia externa.

## Atualizacao Por Fase

### Fase 1

1. Criar `STATE.md` se nao existir.
2. Registrar parametros, arquivos ignorados e fase atual.
3. Salvar resumo tecnico em `phase-1-analysis.md`.
4. Atualizar `STATE.md` com stack, dominio, arquitetura, endpoints detectados e proxima fase.

### Fase 2

1. Atualizar fase para `PHASE_2_AUDIT`.
2. Salvar o relatorio de auditoria no caminho definido.
3. Registrar contagens de severidade, findings e alvos MVC.
4. Atualizar fase para `WAITING_CONFIRMATION`.
5. Manter `Source modifications allowed: NO` ate resposta afirmativa explicita.

### Fase 3

1. Ao receber confirmacao, registrar `Human confirmation for Phase 3: APPROVED` e `Source modifications allowed: YES`.
2. Salvar plano em `refactor-plan.md`.
3. Salvar tarefas em `refactor-tasks.md` e espelhar a tabela no `STATE.md`.
4. Antes de cada tarefa, marcar `IN_PROGRESS`.
5. Apos cada tarefa, registrar arquivos alterados, validacao executada e status.
6. Em falha, marcar `FAILED`, registrar erro e decidir se corrige, pula com justificativa ou bloqueia.
7. Salvar validacao final em `validation-report.md`.

## Retomada

Ao retomar uma execucao:

1. Ler `STATE.md` antes de qualquer outra acao.
2. Verificar se os artefatos apontados em `STATE.md` existem.
3. Conferir `git status` ou equivalente para entender mudancas ja aplicadas.
4. Se `Source modifications allowed` for `NO`, nao editar codigo.
5. Se a fase estiver `WAITING_CONFIRMATION`, pedir confirmacao novamente, salvo se a conversa atual ja contiver aprovacao explicita.
6. Retomar a primeira tarefa `PENDING` ou `FAILED` sem reexecutar tarefas `COMPLETED`, a menos que o usuario peca rerun.
7. Atualizar `STATE.md` antes de encerrar a resposta final.
