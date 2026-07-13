# Fase 1 - Analise do Projeto

## Escopo

- Projeto: `code-smells-project`
- Raiz analisada: `.`
- Arquivos-fonte analisados: 4 (`app.py`, `controllers.py`, `database.py`, `models.py`)
- Manifestos/documentacao operacional: `requirements.txt`, `README.md`
- Exclusoes: `.git`, `.agents`, `.codex`, `reports`, documentacao gerada em `docs/agents`, dependencias, ambientes virtuais, caches, bancos locais e artefatos de build

## Stack Detectada

- Linguagem: Python 3 (versao minima nao declarada)
- Framework HTTP: Flask 3.1.1
- CORS: Flask-Cors 5.0.1
- Banco: SQLite por meio do modulo padrao `sqlite3`
- Inicializacao: `python app.py`
- URL documentada: `http://localhost:5000`
- Testes, ORM, migracoes, schemas de validacao, autenticacao middleware, container e CI: nao detectados

Evidencias: `requirements.txt:1-2`, `README.md:5-12`, `app.py:1-9`, `database.py:1-14`.

## Dominio

API de e-commerce/loja. O dominio e evidenciado por recursos de produtos, usuarios, pedidos, itens de pedido, estoque, login e relatorio de vendas (`app.py:11-30`, `database.py:14-53`).

## Dados e Persistencia

O schema e criado sob demanda dentro de `get_db()` e usa quatro tabelas:

| Tabela | Responsabilidade | Evidencia |
|---|---|---|
| `produtos` | catalogo, preco, estoque e categoria | `database.py:14-25` |
| `usuarios` | identidade, credenciais e tipo | `database.py:26-35` |
| `pedidos` | comprador, status e total | `database.py:36-44` |
| `itens_pedido` | itens, quantidade e preco unitario | `database.py:45-53` |

Dados de exemplo sao inseridos automaticamente quando a tabela `produtos` esta vazia (`database.py:56-84`). A conexao e global, persistente e compartilhada (`database.py:4-11`).

## Arquitetura Atual

Classificacao: monolito procedural em camadas, com MVC parcial apenas nominal.

- `app.py` inicializa Flask e registra rotas, mas tambem implementa views e operacoes administrativas com SQL direto (`app.py:32-78`).
- `controllers.py` recebe requisicoes e serializa respostas, mas tambem valida regras, dispara notificacoes simuladas e consulta SQLite diretamente no health check (`controllers.py:24-62`, `controllers.py:188-220`, `controllers.py:237-255`, `controllers.py:264-292`).
- `models.py` funciona simultaneamente como repository, serializador e service de dominio; cria pedidos, movimenta estoque e calcula relatorio (`models.py:4-314`).
- `database.py` mistura conexao, schema e seed em um singleton global (`database.py:4-86`).

Fluxo predominante: rota Flask -> funcao controller -> funcao em `models.py` -> conexao SQLite global -> dicionario -> `jsonify`.

## Contratos HTTP Detectados

| Metodo | Caminho | Finalidade | Origem |
|---|---|---|---|
| GET | `/` | indice e descoberta da API | `app.py:32-45` |
| GET | `/produtos` | listar produtos | `app.py:11` |
| GET | `/produtos/busca` | buscar/filtrar produtos | `app.py:12` |
| GET | `/produtos/<int:id>` | obter produto | `app.py:13` |
| POST | `/produtos` | criar produto | `app.py:14` |
| PUT | `/produtos/<int:id>` | atualizar produto | `app.py:15` |
| DELETE | `/produtos/<int:id>` | excluir produto | `app.py:16` |
| GET | `/usuarios` | listar usuarios | `app.py:18` |
| GET | `/usuarios/<int:id>` | obter usuario | `app.py:19` |
| POST | `/usuarios` | criar usuario | `app.py:20` |
| POST | `/login` | validar credenciais | `app.py:21` |
| POST | `/pedidos` | criar pedido | `app.py:23` |
| GET | `/pedidos` | listar todos os pedidos | `app.py:24` |
| GET | `/pedidos/usuario/<int:usuario_id>` | listar pedidos por usuario | `app.py:25` |
| PUT | `/pedidos/<int:pedido_id>/status` | atualizar status | `app.py:26` |
| GET | `/relatorios/vendas` | obter relatorio de vendas | `app.py:28` |
| GET | `/health` | diagnostico de aplicacao e banco | `app.py:30` |
| POST | `/admin/reset-db` | apagar todos os dados | `app.py:47-57` |
| POST | `/admin/query` | executar SQL arbitrario | `app.py:59-78` |

## Sinais para a Auditoria

- SQL arbitrario remoto e rotas administrativas sem autenticacao.
- SQL montado por concatenacao com entradas externas.
- senhas em texto puro e expostas por endpoints de usuario.
- chave secreta, debug e metadados internos fixados/expostos.
- conexao global compartilhada, sem fechamento por contexto Flask.
- N+1 na montagem dos pedidos.
- regras de negocio e efeitos colaterais em controllers/models procedurais.
- excecoes internas devolvidas aos clientes.
- criacao de schema e seed durante acesso normal ao banco.
- ausencia completa de testes automatizados.

## Resumo Operacional

```text
================================
FASE 1: ANALISE DO PROJETO
================================
Linguagem:           Python 3
Framework:           Flask 3.1.1
Dependencias:        Flask 3.1.1, Flask-Cors 5.0.1, sqlite3
Dominio:             API de e-commerce/loja
Arquitetura:         Monolito procedural em camadas; MVC parcial com responsabilidades misturadas
Arquivos-fonte:      4 arquivos analisados
Tabelas do banco:    produtos, usuarios, pedidos, itens_pedido
================================
```
