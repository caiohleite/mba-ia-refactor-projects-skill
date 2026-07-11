# Template de Relatório de Auditoria

Use este formato na Fase 2. O relatório deve ser salvo em Markdown e também resumido na conversa. Os achados devem estar ordenados por severidade: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

```markdown
# Relatório de Auditoria Arquitetural - [NOME_DO_PROJETO]

**Gerado em**: [YYYY-MM-DD HH:MM:SS]
**Caminho do projeto**: [caminho/relativo]
**Stack**: [Linguagem + framework]
**Arquivos analisados**: [N]
**LOC aproximado**: [N]
**Domínio**: [domínio]
**Arquitetura atual**: [descrição curta]
**Estado do fluxo de trabalho**: [reports-folder/.refactor-arch/STATE.md]

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | [N] |
| HIGH | [N] |
| MEDIUM | [N] |
| LOW | [N] |

Total de achados: [N]

## Visão Arquitetural

- Ponto de entrada: [arquivo]
- Camada de rotas: [arquivos]
- Camada de dados/modelos: [arquivos]
- Locais com lógica de negócio: [arquivos]
- Pontos de integração/banco de dados: [arquivos]
- Principal risco arquitetural: [uma frase]

## Achados

### [SEVERIDADE] [Título do achado]

- **ID**: [AP-XX]
- **Arquivo**: `[caminho/relativo:início-fim]`
- **Evidência**: [o que foi encontrado]
- **Descrição**: [explicação técnica]
- **Impacto**: [risco para segurança, MVC, manutenibilidade, testes ou performance]
- **Recomendação**: [correção direcionada]
- **Padrão de refatoração**: [nome do padrão no playbook]
- **Confiança**: [Alta|Média|Baixa]

## Achados de APIs Obsoletas

Liste APIs obsoletas/legadas encontradas, ou declare: "Nenhum uso de API obsoleta foi identificado com as evidências disponíveis."

| API | Localização | Uso atual | Equivalente moderno | Confiança |
|---|---|---|---|---|

## Alvos de Refatoração MVC

| Alvo | Localização atual | Destino proposto | Motivo |
|---|---|---|---|

## Plano de Validação para a Fase 3

- Comando de boot: `[comando]`
- Endpoints de smoke test: `[método caminho]`
- Comando de testes: `[comando ou não encontrado]`
- Preparação de dados: `[requisito de seed/migration]`
- Arquivo de estado: `[reports-folder/.refactor-arch/STATE.md]`

## Pré-condições da Fase 3

- O humano revisou este relatório.
- Modificações no código-fonte permanecem desabilitadas até aprovação explícita.
- O contrato dos endpoints foi registrado em `STATE.md`.
- A refatoração deve avançar tarefa por tarefa usando `refactor-plan.md` e `refactor-tasks.md`.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
```

## Regras

- Não iniciar a Fase 3 dentro do relatório.
- Não modificar arquivos de implementação enquanto escreve o relatório.
- Incluir pelo menos 5 achados quando houver evidência suficiente.
- Se houver menos de 5 achados reais, explicar a limitação e não fabricar problemas.
- Relacionar cada achado a um padrão do playbook quando houver transformação aplicável.
- Incluir achados de API obsoleta quando aplicável; se não houver, declarar explicitamente.
- Atualizar `STATE.md` para `WAITING_CONFIRMATION` depois de salvar o relatório.
