# Template De Relatorio De Auditoria

Use este formato na Fase 2. O relatorio deve ser salvo em Markdown e tambem resumido na conversa. Findings devem estar ordenados por severidade: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

```markdown
# Architecture Audit Report - [PROJECT_NAME]

**Generated on**: [YYYY-MM-DD HH:MM:SS]
**Project path**: [relative/path]
**Stack**: [Language + Framework]
**Files analyzed**: [N]
**Approx LOC**: [N]
**Domain**: [domain]
**Current architecture**: [short description]

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | [N] |
| HIGH | [N] |
| MEDIUM | [N] |
| LOW | [N] |

Total findings: [N]

## Architecture Snapshot

- Entry point: [file]
- Routing layer: [files]
- Data/model layer: [files]
- Business logic locations: [files]
- Database/integration points: [files]
- Main architectural risk: [one sentence]

## Findings

### [SEVERITY] [Finding title]

- **ID**: [AP-XX]
- **File**: `[relative/path:start-end]`
- **Evidence**: [what was found]
- **Description**: [technical explanation]
- **Impact**: [risk to security, MVC, maintainability, tests, performance]
- **Recommendation**: [targeted correction]
- **Refactoring pattern**: [playbook pattern name]
- **Confidence**: [High|Medium|Low]

## Deprecated API Findings

List deprecated/legacy APIs found, or state "No deprecated API usage identified with available evidence."

| API | Location | Current usage | Modern equivalent | Confidence |
|---|---|---|---|---|

## MVC Refactoring Targets

| Target | Current location | Proposed destination | Reason |
|---|---|---|---|

## Validation Plan For Phase 3

- Boot command: `[command]`
- Smoke endpoints: `[method path]`
- Test command: `[command or not found]`
- Data setup: `[seed/migration requirement]`

## Confirmation

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras

- Nao iniciar a Fase 3 dentro do relatorio.
- Nao modificar arquivos enquanto escreve o relatorio.
- Incluir pelo menos 5 findings quando houver evidencia suficiente.
- Se houver menos de 5 findings reais, explicar a limitacao e nao fabricar problemas.
- Relacionar cada finding a um padrao do playbook quando houver transformacao aplicavel.
- Incluir findings de API deprecated quando aplicavel; se nao houver, declarar explicitamente.
