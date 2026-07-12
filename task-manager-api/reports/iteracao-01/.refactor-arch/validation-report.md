# Relatório de Validação da Refatoração MVC - task-manager-api

Data: 2026-07-12

## Resultado

**PASS** — aplicação refatorada para MVC, inicialização validada, 22 contratos HTTP registrados e exercitados, e suíte de regressão aprovada.

## Comandos e verificações

| Comando/verificação | Resultado | Evidência |
|---|---|---|
| `venv/bin/python -m unittest discover -s tests -v` | PASS | 4 testes em 4,065s; 0 falhas |
| `env DATABASE_URL=sqlite:///:memory: venv/bin/python seed.py` | PASS | 3 usuários, 4 categorias e 10 tarefas |
| boot `app.py` na porta 5051 com timeout de 3s | PASS | processo permaneceu ativo até exit 124 do timeout |
| parse AST | PASS | 44 arquivos Python relevantes válidos |
| `venv/bin/pip check` | PASS | nenhuma dependência quebrada; apenas aviso de cache sem permissão |
| `git diff --check` | PASS | nenhuma inconsistência de whitespace |
| URL map Flask | PASS | 22 combinações método/caminho, além da rota `static` interna |
| scan de routes/controllers | PASS | nenhum `db`, `.query` ou import de `database` |
| scan de segurança/API legada | PASS | nenhum segredo conhecido, token falso, `query.get`, `datetime.utcnow` ou `except:` nu |
| scan de DTOs em models/camadas HTTP | PASS | nenhum `to_dict` em model nem chave `password` em serializers/controllers/routes |

O primeiro boot real dentro do sandbox falhou com `PermissionError` ao abrir socket. A mesma execução autorizada fora da restrição permaneceu ativa até o timeout, confirmando o boot. Essa falha inicial foi ambiental, não da aplicação.

## Contratos HTTP

| Grupo | Métodos/caminhos | Resultado |
|---|---|---|
| Saúde | `GET /`, `GET /health` | 200 |
| Tarefas | `GET/POST /tasks`; `GET/PUT/DELETE /tasks/<id>`; `GET /tasks/search`; `GET /tasks/stats` | PASS; mutações exigem token |
| Usuários | `GET/POST /users`; `GET/PUT/DELETE /users/<id>`; `GET /users/<id>/tasks` | PASS; acesso sensível autenticado/autorizado |
| Autenticação | `POST /login` | 200; token assinado e DTO sem senha |
| Relatórios | `GET /reports/summary`; `GET /reports/user/<id>` | PASS; papéis/identidade verificados |
| Categorias | `GET/POST /categories`; `PUT/DELETE /categories/<id>` | PASS; mutações exigem admin |
| Falhas de segurança | rotas protegidas sem token/com papel insuficiente | 401/403 conforme esperado |
| Validação | payload, prioridade, email e recurso inexistente | 400/404 JSON padronizado |

## Regressão Arquitetural

- Application factory e raiz de composição: `app.py`.
- Configuração por ambiente e segredo gerado com entropia quando não configurado: `config.py`.
- Models limitados a ORM e invariantes.
- Repositories concentram SQLAlchemy, eager loading e agregações.
- Services concentram regras, transações e casos de uso sem Flask.
- Controllers adaptam HTTP e escolhem DTOs.
- Routes registram endpoints/decorators sem persistência ou regras pesadas.
- Middlewares centralizam autenticação, autorização e erros.
- Schemas centralizam constantes, validações e DTOs seguros.

## Cobertura Final dos Achados

| ID | Resultado | Evidência principal |
|---|---|---|
| AP-02 | FIXED | `config.py`; SMTP via ambiente; scans sem credenciais fixas |
| AP-03 | FIXED | Bearer token, roles e testes 401/403/sucesso |
| AP-07 | FIXED | Werkzeug scrypt e token assinado; MD5 apenas para migração automática de registros antigos |
| AP-08 | FIXED | DTO público sem senha e testes de resposta |
| AP-04 | FIXED | routes/controllers/services/repositories/schemas separados |
| AP-05 | FIXED | regras movidas para services |
| AP-06 | FIXED | persistência encapsulada em repositories |
| AP-09 | FIXED | eager loading e agregações, sem query em loop de entidade |
| AP-11 | FIXED | validators/constants/serializers centralizados |
| AP-12 | FIXED | exceções tipadas e error handler central |
| AP-13 | FIXED | `db.session.get`; UTC explícito compatível com schema SQLite atual |
| AP-14 | FIXED | nomes de domínio e constantes compartilhadas |
| AP-15 | FIXED | imports/resíduos removidos; dependências diretas não usadas retiradas do manifesto |

## Checklist Obrigatório

### Fase 1
- [x] Linguagem, framework e domínio detectados.
- [x] 15 arquivos-fonte originais contabilizados.

### Fase 2
- [x] Relatório no modelo obrigatório.
- [x] 13 achados com linhas e severidade ordenada.
- [x] APIs legadas identificadas.
- [x] Pausa e confirmação humana registradas.

### Fase 3
- [x] Estrutura MVC implementada.
- [x] Configuração sem segredo fixo.
- [x] Models/repositories isolam dados.
- [x] Routes e controllers sem ORM.
- [x] Erros e autenticação centralizados.
- [x] Ponto de entrada claro.
- [x] Aplicação inicia.
- [x] Endpoints originais respondem.

## Mudanças de Contrato Aprovadas por Segurança

- Operações sensíveis agora exigem `Authorization: Bearer <token>` e, quando aplicável, papel `admin`/`manager` ou identidade do próprio usuário.
- Respostas de usuário não incluem mais o campo `password`.
- O token falso foi substituído por token assinado com expiração configurável.

## Limitações e Riscos Residuais

- Usuários com hashes MD5 no banco existente são migrados para hash forte somente após um login válido; novos hashes já usam scrypt.
- Se `SECRET_KEY` não for definida no ambiente, uma chave aleatória é gerada a cada processo e tokens anteriores deixam de valer após restart. Produção deve configurar uma chave persistente.
- O envio SMTP não foi exercitado por depender de credenciais/serviço externo; sem configuração, o serviço falha de forma segura e não tenta autenticar.
- Datas continuam armazenadas como datetime ingênuo no schema SQLite legado, mas são geradas a partir de UTC explícito para evitar alteração de schema nesta refatoração.
