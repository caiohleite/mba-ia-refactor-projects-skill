# Controle de Estado e Recuperação

Use este guia em todas as fases da skill `refactor-arch`. O objetivo é permitir retomada precisa após interrupção, sem repetir etapas concluídas nem perder controle das tarefas executadas.

## Artefatos Gerados

Crie e mantenha estes artefatos dentro de `reports-folder/.refactor-arch/`:

```text
reports-folder/
|-- audit-[nome-do-projeto].md
`-- .refactor-arch/
    |-- STATE.md
    |-- phase-1-analysis.md
    |-- refactor-plan.md
    |-- refactor-tasks.md
    `-- validation-report.md
```

Antes da confirmação da Fase 2, somente estes artefatos de fluxo de trabalho e o relatório de auditoria podem ser criados ou atualizados. Código-fonte, arquivos de manifesto, lockfiles, configuração da aplicação e banco de dados não devem ser alterados antes da confirmação explícita.

## STATE.md

`STATE.md` é a fonte de verdade para retomada. Atualize-o no início e no fim de cada fase, antes e depois de cada tarefa de refatoração, e sempre que uma validação falhar.

Modelo:

```markdown
# Estado da Refatoração Arquitetural - [NOME_DO_PROJETO]

Gerado em: [YYYY-MM-DD HH:MM:SS]
Última atualização: [YYYY-MM-DD HH:MM:SS]

## Parâmetros
- Pasta do projeto: [caminho]
- Pasta de relatórios: [caminho]
- Nome do relatório: [arquivo de auditoria]
- Pastas ignoradas: [itens]
- URL base de validação: [url ou não informada]

## Status de Execução
- Fase atual: [PHASE_1_ANALYSIS|PHASE_2_AUDIT|WAITING_CONFIRMATION|PHASE_3_PLANNING|PHASE_3_TASKS|PHASE_3_IMPLEMENTATION|PHASE_3_VALIDATION|COMPLETED|PARTIAL|BLOCKED]
- Modificações no código-fonte permitidas: [NO|YES]
- Confirmação humana para a Fase 3: [PENDING|APPROVED|DECLINED]
- Última etapa concluída: [descrição curta]
- Próxima etapa: [descrição curta]

## Artefatos
- Análise da Fase 1: [caminho ou PENDING]
- Relatório de auditoria: [caminho ou PENDING]
- Plano de refatoração: [caminho ou PENDING]
- Lista de tarefas: [caminho ou PENDING]
- Relatório de validação: [caminho ou PENDING]

## Resumo dos Achados
- CRITICAL: [N]
- HIGH: [N]
- MEDIUM: [N]
- LOW: [N]

## Cobertura dos Achados
| ID do achado | Severidade | Decisão | Etapa do plano | IDs das tarefas | Validação | Observações |
|---|---|---|---|---|---|---|
| AP-XX | HIGH | FIX | P02 | T03,T04 | teste de fumaça/teste/verificação | observações |

## Tarefas de Refatoração
| ID | Status | Etapa do plano | IDs dos achados | Arquivos | Validação | Observações |
|---|---|---|---|---|---|---|
| T01 | PENDING | P01 | AP-XX | caminho | comando/verificação | observações |

## Contrato dos Endpoints
| Método | Caminho | Finalidade | Origem | Status |
|---|---|---|---|---|

## Log de Validação
| Horário | Comando/Verificação | Resultado | Observações |
|---|---|---|---|

## Erros e Notas de Recuperação
- [timestamp] [erro ou decisão]
```

## Regras de Status

- `PENDING`: ainda não iniciado.
- `IN_PROGRESS`: em execução agora.
- `COMPLETED`: concluído e validado.
- `FAILED`: executado com erro; exige correção ou decisão.
- `SKIPPED`: omitido com justificativa explícita.
- `BLOCKED`: impossível avançar sem entrada humana ou dependência externa.

## Atualização por Fase

### Fase 1

1. Criar `STATE.md` se não existir.
2. Registrar parâmetros, arquivos ignorados e fase atual.
3. Salvar resumo técnico em `phase-1-analysis.md`.
4. Atualizar `STATE.md` com stack, domínio, arquitetura, endpoints detectados e próxima fase.

### Fase 2

1. Atualizar fase para `PHASE_2_AUDIT`.
2. Salvar o relatório de auditoria no caminho definido.
3. Registrar contagens de severidade, achados e alvos MVC.
4. Atualizar fase para `WAITING_CONFIRMATION`.
5. Manter `Modificações no código-fonte permitidas: NO` até resposta afirmativa explícita.

### Fase 3

1. Ao receber confirmação, registrar `Confirmação humana para a Fase 3: APPROVED` e `Modificações no código-fonte permitidas: YES`.
2. Salvar plano em `refactor-plan.md`.
3. Registrar em `Cobertura dos Achados` uma decisão para cada achado aprovado do relatório.
4. Salvar tarefas em `refactor-tasks.md` e espelhar a tabela no `STATE.md`.
5. Antes de cada tarefa, marcar `IN_PROGRESS`.
6. Após cada tarefa, registrar arquivos alterados, validação executada e status.
7. Em falha, marcar `FAILED`, registrar erro e decidir se corrige, pula com justificativa ou bloqueia.
8. Salvar validação final em `validation-report.md`.

## Retomada

Ao retomar uma execução:

1. Ler `STATE.md` antes de qualquer outra ação.
2. Verificar se os artefatos apontados em `STATE.md` existem.
3. Conferir `git status` ou equivalente para entender mudanças já aplicadas.
4. Se `Modificações no código-fonte permitidas` for `NO`, não editar código.
5. Se a fase estiver `WAITING_CONFIRMATION`, pedir confirmação novamente, salvo se a conversa atual já contiver aprovação explícita.
6. Retomar a primeira tarefa `PENDING` ou `FAILED` sem reexecutar tarefas `COMPLETED`, a menos que o usuário peça reexecução.
7. Atualizar `STATE.md` antes de encerrar a resposta final.
