# Estado da Refatoração Arquitetural - code-smells-project

Gerado em: 2026-07-11
Última atualização: 2026-07-11 (Fase 2 concluída)

## Parâmetros
- Pasta do projeto: `.`
- Pasta de relatórios: `reports`
- Nome do relatório: `audit-code-smells-project.md`
- Pastas ignoradas: `.git`, `node_modules`, ambientes virtuais, caches, `dist`, `build`, bancos locais gerados e artefatos gerados
- URL base de validação: não informada

## Status de Execução
- Fase atual: WAITING_CONFIRMATION
- Modificações no código-fonte permitidas: NO
- Confirmação humana para a Fase 3: PENDING
- Última etapa concluída: Fase 2 — auditoria salva e suíte de regressão aprovada
- Próxima etapa: aguardar confirmação humana; para objetivo estritamente MVC, a recomendação é não refatorar

## Artefatos
- Análise da Fase 1: `reports/.refactor-arch/phase-1-analysis.md`
- Relatório de auditoria: `reports/audit-code-smells-project.md`
- Plano de refatoração: PENDING
- Lista de tarefas: PENDING
- Relatório de validação: PENDING

## Resumo dos Achados
- CRITICAL: 2
- HIGH: 1
- MEDIUM: 2
- LOW: 2

## Cobertura dos Achados
| ID do achado | Severidade | Decisão | Etapa do plano | IDs das tarefas | Validação | Observações |
|---|---|---|---|---|---|---|
| AP-02 | CRITICAL | PENDING | PENDING | PENDING | login/seed | credenciais previsíveis no seed |
| AP-03 | CRITICAL | PENDING | PENDING | PENDING | testes de autorização | operações mutáveis sem guard |
| AP-08 | HIGH | PENDING | PENDING | PENDING | testes de ownership/papel | PII e pedidos enumeráveis |
| AP-06A | MEDIUM | PENDING | PENDING | PENDING | testes de constraints | integridade relacional ausente |
| AP-06B | MEDIUM | PENDING | PENDING | PENDING | inicialização/CLI | DDL e seed no boot |
| AP-14 | LOW | PENDING | PENDING | PENDING | testes unitários de limites | números mágicos de desconto |
| AP-15 | LOW | PENDING | PENDING | PENDING | CRUD/listagem de produto | política de `ativo` indefinida |

## Tarefas de Refatoração
| ID | Status | Etapa do plano | IDs dos achados | Arquivos | Validação | Observações |
|---|---|---|---|---|---|---|

## Contrato dos Endpoints
| Método | Caminho | Finalidade | Origem | Status |
|---|---|---|---|---|
| GET | `/` | índice da API | `loja/views/system_routes.py:11` | PRESERVED |
| GET | `/health` | saúde sanitizada | `loja/views/system_routes.py:16` | PRESERVED |
| GET | `/produtos` | listar produtos | `loja/views/product_routes.py:11` | PRESERVED |
| GET | `/produtos/busca` | buscar produtos | `loja/views/product_routes.py:16` | PRESERVED |
| GET | `/produtos/<int:id>` | obter produto | `loja/views/product_routes.py:21` | PRESERVED |
| POST | `/produtos` | criar produto | `loja/views/product_routes.py:26` | PRESERVED |
| PUT | `/produtos/<int:id>` | atualizar produto | `loja/views/product_routes.py:31` | PRESERVED |
| DELETE | `/produtos/<int:id>` | excluir produto | `loja/views/product_routes.py:36` | PRESERVED |
| GET | `/usuarios` | listar usuários | `loja/views/user_routes.py:11` | PRESERVED |
| GET | `/usuarios/<int:id>` | obter usuário | `loja/views/user_routes.py:16` | PRESERVED |
| POST | `/usuarios` | criar usuário | `loja/views/user_routes.py:21` | PRESERVED |
| POST | `/login` | autenticar usuário | `loja/views/user_routes.py:26` | PRESERVED |
| POST | `/pedidos` | criar pedido | `loja/views/order_routes.py:13` | PRESERVED |
| GET | `/pedidos` | listar pedidos | `loja/views/order_routes.py:18` | PRESERVED |
| GET | `/pedidos/usuario/<int:usuario_id>` | listar pedidos por usuário | `loja/views/order_routes.py:23` | PRESERVED |
| PUT | `/pedidos/<int:pedido_id>/status` | alterar status | `loja/views/order_routes.py:28` | PRESERVED |
| GET | `/relatorios/vendas` | relatório de vendas | `loja/views/order_routes.py:33` | PRESERVED |
| POST | `/admin/reset-db` | reset autenticado | `loja/views/system_routes.py:21` | PRESERVED |
| POST | `/admin/query` | recusar SQL arbitrário | `loja/views/system_routes.py:31` | PRESERVED |

## Log de Validação
| Horário | Comando/Verificação | Resultado | Observações |
|---|---|---|---|
| 2026-07-11 | `git status --short --branch` | PASS | árvore limpa antes da análise (`refactor/refatora-002`) |
| 2026-07-11 | inventário e leitura dos 35 arquivos Python | PASS | 30 arquivos com código relevante e 5 marcadores de pacote |
| 2026-07-11 | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` | PASS | 7 testes aprovados em 2,436 s; erro interno simulado foi sanitizado como esperado |
| 2026-07-11 | varredura de APIs legadas do catálogo | PASS | nenhum uso aplicável encontrado |

## Erros e Notas de Recuperação
- 2026-07-11: execução iniciada; nenhuma modificação no código-fonte está autorizada.
- 2026-07-11: Fase 1 concluída; arquitetura atual classificada como MVC/em camadas, sujeita à auditoria da Fase 2.
- 2026-07-11: Fase 2 concluída com 7 achados; nenhuma alteração de código-fonte realizada.
- 2026-07-11: reestruturação MVC avaliada como desnecessária; correções localizadas de segurança continuam recomendadas.
