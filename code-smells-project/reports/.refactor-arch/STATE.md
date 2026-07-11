# Estado da Refatoracao Arquitetural - code-smells-project

Gerado em: 2026-07-10 22:36:37 -0300
Ultima atualizacao: 2026-07-10 22:39:25 -0300

## Parametros
- Pasta do projeto: `.`
- Pasta de relatorios: `reports`
- Nome do relatorio: `audit-code-smells-project.md`
- Pastas ignoradas: `.git`, `.agents`, `.codex`, `reports`, `node_modules`, `venv`, `.venv`, `__pycache__`, `.pytest_cache`, `dist`, `build`
- URL base de validacao: nao informada

## Status de Execucao
- Fase atual: `WAITING_CONFIRMATION`
- Modificacoes no codigo-fonte permitidas: `NO`
- Confirmacao humana para a Fase 3: `PENDING`
- Ultima etapa concluida: Fase 2 concluida; 14 achados auditados e relatorio salvo
- Proxima etapa: aguardar confirmacao humana explicita para iniciar o planejamento da Fase 3

## Artefatos
- Analise da Fase 1: `reports/.refactor-arch/phase-1-analysis.md`
- Relatorio de auditoria: `reports/audit-code-smells-project.md`
- Plano de refatoracao: `PENDING`
- Lista de tarefas: `PENDING`
- Relatorio de validacao: `PENDING`

## Resumo dos Achados
- CRITICAL: 5
- HIGH: 4
- MEDIUM: 3
- LOW: 2

## Cobertura dos Achados
| ID do achado | Severidade | Decisao | Etapa do plano | IDs das tarefas | Validacao | Observacoes |
|---|---|---|---|---|---|---|
| AP-01 | CRITICAL | PENDING | PENDING | PENDING | PENDING | SQL dinamico e endpoint de SQL arbitrario |
| AP-03 | CRITICAL | PENDING | PENDING | PENDING | PENDING | endpoints administrativos sem protecao |
| AP-07 | CRITICAL | PENDING | PENDING | PENDING | PENDING | senhas em texto puro |
| AP-02 | CRITICAL | PENDING | PENDING | PENDING | PENDING | segredo/debug fixados e expostos |
| AP-08 | CRITICAL | PENDING | PENDING | PENDING | PENDING | senhas em respostas publicas |
| AP-04 | HIGH | PENDING | PENDING | PENDING | PENDING | arquivo Deus de dados e dominio |
| AP-06 | HIGH | PENDING | PENDING | PENDING | PENDING | persistencia e dominio misturados |
| AP-05 | HIGH | PENDING | PENDING | PENDING | PENDING | regras e efeitos em controllers |
| AP-10 | HIGH | PENDING | PENDING | PENDING | PENDING | conexao SQLite global |
| AP-09 | MEDIUM | PENDING | PENDING | PENDING | PENDING | consultas N+1 em pedidos |
| AP-12 | MEDIUM | PENDING | PENDING | PENDING | PENDING | erros duplicados e expostos |
| AP-11 | MEDIUM | PENDING | PENDING | PENDING | PENDING | validacao duplicada/incompleta |
| AP-14 | LOW | PENDING | PENDING | PENDING | PENDING | valores magicos |
| AP-15 | LOW | PENDING | PENDING | PENDING | PENDING | imports mortos e prints |

## Tarefas de Refatoracao
| ID | Status | Etapa do plano | IDs dos achados | Arquivos | Validacao | Observacoes |
|---|---|---|---|---|---|---|

## Contrato dos Endpoints
| Metodo | Caminho | Finalidade | Origem | Status |
|---|---|---|---|---|
| GET | `/` | indice e descoberta da API | `app.py:32-45` | BASELINE |
| GET | `/produtos` | listar produtos | `app.py:11` | BASELINE |
| GET | `/produtos/busca` | buscar/filtrar produtos | `app.py:12` | BASELINE |
| GET | `/produtos/<int:id>` | obter produto | `app.py:13` | BASELINE |
| POST | `/produtos` | criar produto | `app.py:14` | BASELINE |
| PUT | `/produtos/<int:id>` | atualizar produto | `app.py:15` | BASELINE |
| DELETE | `/produtos/<int:id>` | excluir produto | `app.py:16` | BASELINE |
| GET | `/usuarios` | listar usuarios | `app.py:18` | BASELINE |
| GET | `/usuarios/<int:id>` | obter usuario | `app.py:19` | BASELINE |
| POST | `/usuarios` | criar usuario | `app.py:20` | BASELINE |
| POST | `/login` | validar credenciais | `app.py:21` | BASELINE |
| POST | `/pedidos` | criar pedido | `app.py:23` | BASELINE |
| GET | `/pedidos` | listar todos os pedidos | `app.py:24` | BASELINE |
| GET | `/pedidos/usuario/<int:usuario_id>` | listar pedidos por usuario | `app.py:25` | BASELINE |
| PUT | `/pedidos/<int:pedido_id>/status` | atualizar status | `app.py:26` | BASELINE |
| GET | `/relatorios/vendas` | obter relatorio de vendas | `app.py:28` | BASELINE |
| GET | `/health` | diagnostico de aplicacao e banco | `app.py:30` | BASELINE |
| POST | `/admin/reset-db` | apagar todos os dados | `app.py:47-57` | BASELINE |
| POST | `/admin/query` | executar SQL arbitrario | `app.py:59-78` | BASELINE |

## Log de Validacao
| Horario | Comando/Verificacao | Resultado | Observacoes |
|---|---|---|---|
| 2026-07-10 22:36:37 -0300 | `git status --short` | PASS | Arvore de trabalho limpa antes da analise |
| 2026-07-10 22:39:00 -0300 | inventario estatico da Fase 1 | PASS | 4 arquivos-fonte, 19 endpoints e 4 tabelas mapeados |
| 2026-07-10 22:39:25 -0300 | `python app.py` | NOT_RUN | comando `python` ausente no ambiente |
| 2026-07-10 22:39:25 -0300 | importacao com `PYTHONDONTWRITEBYTECODE=1 python3` | PASS | Flask importou e registrou 19 endpoints; nenhum banco/cache criado |
| 2026-07-10 22:39:25 -0300 | auditoria estatica contra AP-01 a AP-15 | PASS | 14 achados com localizacao e recomendacao |

## Erros e Notas de Recuperacao
- 2026-07-10 22:36:37 -0300: nenhuma execucao anterior detectada; codigo-fonte permanece bloqueado ate confirmacao explicita.
- 2026-07-10 22:39:25 -0300: Fase 2 encerrada; mudancas observaveis de seguranca estao descritas no relatorio e dependem de aprovacao.
- 2026-07-10 22:39:25 -0300: modificacoes no codigo-fonte permanecem bloqueadas (`NO`).
