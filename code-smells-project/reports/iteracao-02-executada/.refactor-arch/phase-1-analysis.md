# Fase 1 — Análise do Projeto

## Escopo

- Projeto: `code-smells-project`
- Raiz analisada: `.`
- Exclusões: `.git`, `.agents`, `.codex`, `reports`, `docs/agents`, `venv`, caches, bancos locais e artefatos gerados
- Arquivos inspecionados: 35 arquivos Python; 30 contêm código relevante e 5 são marcadores de pacote
- Manifestos/documentação operacional: `requirements.txt` e `README.md`

## Stack e execução

- Linguagem: Python 3 (type hints como `list[OrderItem]` requerem Python 3.9+)
- Framework HTTP: Flask 3.1.1
- Extensão: flask-cors 5.0.1
- Banco: SQLite via `sqlite3` da biblioteca padrão
- Segurança de senhas: `werkzeug.security`
- Ponto de entrada: `app.py`; cria a aplicação pela factory `loja.create_app`
- Inicialização: `python app.py` ou `python3 app.py`
- Testes: `python3 -m unittest discover -v`

## Domínio inferido

API de e-commerce com catálogo de produtos, usuários/login, pedidos e itens, estoque, relatório de vendas, saúde da aplicação e operações administrativas. A inferência vem das entidades em `loja/models.py`, das tabelas em `loja/database.py` e das rotas registradas pelos blueprints em `loja/views/`.

## Persistência

Tabelas detectadas:

- `produtos`
- `usuarios`
- `pedidos`
- `itens_pedido`

O schema e os seeds são inicializados no primeiro boot por `loja.database.init_database`. O acesso SQL está isolado principalmente em `loja/repositories/`; consultas recebem parâmetros, inclusive os filtros de busca e a lista dinâmica de IDs.

## Arquitetura real

Classificação: **MVC/em camadas já implementado**, com pequenos pontos candidatos a aperfeiçoamento, não um monolito procedural.

Fluxo principal observado:

`Blueprint/view HTTP -> Controller -> Service -> Repository -> SQLite`

- `app.py` é um entrypoint fino.
- `loja/__init__.py` contém a application factory e registra infraestrutura/blueprints.
- `loja/views/` adapta request/response e registra rotas.
- `loja/controllers/` coordena casos de uso e monta os envelopes HTTP.
- `loja/services/` contém validação, regras de negócio e fronteiras transacionais.
- `loja/repositories/` concentra SQL e materialização dos modelos.
- `loja/models.py` define entidades/DTOs e serialização.
- `loja/errors.py` centraliza respostas de erro.

Os nomes das pastas correspondem ao comportamento real. Não foram observadas rotas consultando o banco diretamente, controllers executando SQL, SQL arbitrário habilitado, respostas expondo hash de senha ou configuração sensível, nem arquivo Deus.

## Contrato HTTP detectado

| Método | Caminho | Finalidade | Origem |
|---|---|---|---|
| GET | `/` | índice e descoberta da API | `loja/views/system_routes.py:11` |
| GET | `/health` | saúde e contagens sanitizadas | `loja/views/system_routes.py:16` |
| GET | `/produtos` | listar produtos | `loja/views/product_routes.py:11` |
| GET | `/produtos/busca` | buscar produtos | `loja/views/product_routes.py:16` |
| GET | `/produtos/<int:id>` | obter produto | `loja/views/product_routes.py:21` |
| POST | `/produtos` | criar produto | `loja/views/product_routes.py:26` |
| PUT | `/produtos/<int:id>` | atualizar produto | `loja/views/product_routes.py:31` |
| DELETE | `/produtos/<int:id>` | excluir produto | `loja/views/product_routes.py:36` |
| GET | `/usuarios` | listar usuários sem senha | `loja/views/user_routes.py:11` |
| GET | `/usuarios/<int:id>` | obter usuário sem senha | `loja/views/user_routes.py:16` |
| POST | `/usuarios` | criar usuário | `loja/views/user_routes.py:21` |
| POST | `/login` | autenticar usuário | `loja/views/user_routes.py:26` |
| POST | `/pedidos` | criar pedido | `loja/views/order_routes.py:13` |
| GET | `/pedidos` | listar pedidos | `loja/views/order_routes.py:18` |
| GET | `/pedidos/usuario/<int:usuario_id>` | listar pedidos por usuário | `loja/views/order_routes.py:23` |
| PUT | `/pedidos/<int:pedido_id>/status` | alterar status do pedido | `loja/views/order_routes.py:28` |
| GET | `/relatorios/vendas` | relatório de vendas | `loja/views/order_routes.py:33` |
| POST | `/admin/reset-db` | reset administrativo autenticado | `loja/views/system_routes.py:21` |
| POST | `/admin/query` | contrato legado que recusa SQL arbitrário | `loja/views/system_routes.py:31` |

## Sinais encaminhados à auditoria

- autenticação de login não gera sessão/token e a maior parte dos endpoints mutáveis não possui autorização;
- CORS é aplicado sem política explícita de origens;
- integridade relacional depende mais da aplicação do que do schema, que não declara chaves estrangeiras/índices únicos;
- services conhecem diretamente `get_db()` para commits/transações, acoplando regra de negócio à infraestrutura SQLite/Flask;
- serialização está nas entidades de domínio, o que pode ser aceitável em projeto pequeno, mas merece avaliação de separação de responsabilidades;
- schema e seed são executados durante a criação da aplicação, sem migrações versionadas.

## Resumo operacional

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:           Python 3
Framework:           Flask 3.1.1
Dependências:        Flask, flask-cors, Werkzeug (transitiva), sqlite3 (stdlib)
Domínio:             E-commerce (produtos, usuários, pedidos, estoque e vendas)
Arquitetura:         MVC/em camadas já implementado; pontos menores seguem para auditoria
Arquivos-fonte:      30 arquivos relevantes analisados (35 Python inspecionados)
Tabelas do banco:    produtos, usuarios, pedidos, itens_pedido
================================
```
