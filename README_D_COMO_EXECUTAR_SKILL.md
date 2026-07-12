# Como Executar a Skill `refactor-arch`

Este documento cobre somente a seção **D) Como Executar** solicitada no `README.md`: pré-requisitos, comandos para executar a skill `refactor-arch` em cada projeto e validações necessárias para confirmar que a refatoração funcionou.

## Pré-requisitos

- OpenAI Codex CLI instalado, autenticado e configurado.
- Execução iniciada a partir da raiz de cada projeto, não da raiz do repositório pai.
- Skill disponível no projeto em `.agents/skills/refactor-arch/`.
- Agentes personalizados disponíveis no projeto em `.codex/agents/refactor-*.toml`.
- Dependências do projeto instaláveis conforme o `README.md` de cada aplicação.
- Árvore de trabalho revisada antes da execução, pois a Fase 3 altera código-fonte após confirmação.

Os três projetos já possuem a skill e os agentes nos caminhos esperados:

| Projeto | Skill | Agentes |
|---|---|---|
| `code-smells-project` | `code-smells-project/.agents/skills/refactor-arch/` | `code-smells-project/.codex/agents/` |
| `ecommerce-api-legacy` | `ecommerce-api-legacy/.agents/skills/refactor-arch/` | `ecommerce-api-legacy/.codex/agents/` |
| `task-manager-api` | `task-manager-api/.agents/skills/refactor-arch/` | `task-manager-api/.codex/agents/` |

## Forma de invocação no Codex

No Codex CLI, a skill deve ser chamada pelo nome `$refactor-arch`. O comando abaixo deve ser enviado como mensagem dentro da interface do Codex, já posicionado na raiz do projeto alvo:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: [NOME_DO_RELATORIO]
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Ao final da Fase 2, revise o relatório de auditoria gerado. Se estiver correto e você quiser aplicar a refatoração, responda no Codex:

```text
s
```

Se a resposta não for afirmativa, a skill deve encerrar sem alterar o código-fonte.

## Projeto 1: `code-smells-project`

Entre na raiz do projeto:

```bash
cd code-smells-project
```

No Codex CLI, envie:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: audit-project-1.md
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Após revisar `reports/audit-project-1.md`, responda `s` para executar a Fase 3.

Valide a execução da skill verificando:

- `reports/audit-project-1.md`;
- `reports/.refactor-arch/STATE.md`;
- `reports/.refactor-arch/phase-1-analysis.md`;
- `reports/.refactor-arch/refactor-plan.md`;
- `reports/.refactor-arch/refactor-tasks.md`;
- `reports/.refactor-arch/validation-report.md`.

Para validar a aplicação refatorada, siga o `README.md` do projeto. Em resumo:

```bash
python3 -m pip install -r requirements.txt
flask --app app init-db
python3 app.py
curl http://localhost:5000/health
python3 -m unittest discover -v
```

O comando `python3 app.py` mantém o servidor em primeiro plano. Execute o `curl` em outro terminal ou interrompa o servidor antes de rodar a suíte de testes.

No Windows, use `python` no lugar de `python3` se esse for o executável disponível.

## Projeto 2: `ecommerce-api-legacy`

Entre na raiz do projeto:

```bash
cd ecommerce-api-legacy
```

No Codex CLI, envie:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: audit-project-2.md
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Após revisar `reports/audit-project-2.md`, responda `s` para executar a Fase 3.

Valide a execução da skill verificando:

- `reports/audit-project-2.md`;
- `reports/.refactor-arch/STATE.md`;
- `reports/.refactor-arch/phase-1-analysis.md`;
- `reports/.refactor-arch/refactor-plan.md`;
- `reports/.refactor-arch/refactor-tasks.md`;
- `reports/.refactor-arch/validation-report.md`.

Para validar a aplicação refatorada, siga o `README.md` do projeto. Em resumo:

```bash
npm ci
npm test
npm start
```

O comando `npm start` mantém o servidor em primeiro plano. Com o servidor ativo, valide os endpoints em outro terminal usando o arquivo `api.http` ou requisições `curl` descritas no `README.md`, especialmente:

- `POST /api/checkout`;
- `GET /api/admin/financial-report` com `ADMIN_API_KEY`;
- `DELETE /api/users/:id` com `ADMIN_API_KEY`.

## Projeto 3: `task-manager-api`

Entre na raiz do projeto:

```bash
cd task-manager-api
```

No Codex CLI, envie:

```text
Use $refactor-arch neste projeto.
Parâmetros:
- project-folder: .
- reports-folder: reports
- report-name: audit-project-3.md
Execute as Fases 1 e 2. Ao concluir a Fase 2, pause e solicite confirmação antes da Fase 3.
```

Após revisar `reports/audit-project-3.md`, responda `s` para executar a Fase 3.

Valide a execução da skill verificando:

- `reports/audit-project-3.md`;
- `reports/.refactor-arch/STATE.md`;
- `reports/.refactor-arch/phase-1-analysis.md`;
- `reports/.refactor-arch/refactor-plan.md`;
- `reports/.refactor-arch/refactor-tasks.md`;
- `reports/.refactor-arch/validation-report.md`.

Para validar a aplicação refatorada, siga o `README.md` do projeto. Em resumo:

```bash
python3 -m pip install -r requirements.txt
python3 seed.py
python3 app.py
curl http://localhost:5000/health
python3 -m unittest discover -v
```

O comando `python3 app.py` mantém o servidor em primeiro plano. Execute o `curl` em outro terminal ou interrompa o servidor antes de rodar a suíte de testes.

O seed é opcional para a API iniciar, mas ajuda a validar fluxos autenticados e endpoints com dados de demonstração.

## Checklist de validação da skill

Após executar a skill em cada projeto, confirme:

- A Fase 1 detectou linguagem, framework, domínio e arquitetura atual corretamente.
- A Fase 2 gerou o relatório no nome esperado (`audit-project-1.md`, `audit-project-2.md` ou `audit-project-3.md`).
- O relatório contém pelo menos 5 achados quando houver evidência suficiente.
- Os achados estão classificados por severidade (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) e incluem arquivo/linha quando aplicável.
- A skill pausou ao final da Fase 2 e só iniciou a Fase 3 após resposta afirmativa.
- A Fase 3 gerou `refactor-plan.md`, `refactor-tasks.md` e `validation-report.md`.
- `STATE.md` registra a fase final, tarefas executadas, validações e eventuais limitações.
- A aplicação inicia sem erros depois da refatoração.
- Os endpoints originais principais continuam respondendo.
- Os testes automatizados do projeto passam, ou qualquer impedimento está documentado em `validation-report.md`.

## Retomada após interrupção

Se a execução for interrompida, reabra o Codex CLI na raiz do mesmo projeto e envie:

```text
Use $refactor-arch para retomar a execução deste projeto a partir de reports/.refactor-arch/STATE.md.
Não reinicie tarefas concluídas; continue da primeira fase ou tarefa PENDING ou FAILED.
```

A skill deve ler `reports/.refactor-arch/STATE.md` antes de agir, preservar tarefas já concluídas e respeitar o campo `Modificações no código-fonte permitidas`.

## Observações importantes

- Execute a skill separadamente em cada projeto.
- Não execute a skill a partir da raiz do repositório pai quando o objetivo for refatorar apenas um projeto.
- Antes de confirmar a Fase 3, revise o relatório de auditoria e os riscos identificados.
- Em projetos já refatorados, uma nova execução audita o estado atual; para reproduzir a refatoração desde o início, use uma cópia limpa do projeto legado.
- As instruções completas de instalação, variáveis de ambiente, endpoints e testes pertencem ao `README.md` de cada projeto. Este documento registra apenas o fluxo de execução da skill e os pontos de validação relacionados a ela.
