# Catalogo De Anti-Patterns

Use este catalogo na Fase 2. Cada finding deve ter evidencia concreta, severidade, impacto e recomendacao. Classifique pela pior consequencia comprovada no contexto.

## Escala De Severidade

- **CRITICAL**: falha grave de seguranca ou arquitetura que pode expor dados, permitir execucao/consulta indevida, corromper dados ou violar totalmente separacao de responsabilidades.
- **HIGH**: forte violacao de MVC/SOLID, acoplamento alto ou fragilidade que dificulta manutencao, teste e evolucao.
- **MEDIUM**: duplicacao, performance ruim, validacao incompleta, APIs legadas ou desenho que causa custo moderado.
- **LOW**: legibilidade, nomenclatura, magic numbers, imports mortos e pequenos problemas de organizacao.

## Anti-Patterns Obrigatorios

| ID | Anti-pattern | Severidade base | Sinais de deteccao | Recomendacao |
|---|---|---:|---|---|
| AP-01 | SQL Injection / query dinamica insegura | CRITICAL | SQL montado por concatenacao, template string ou interpolacao com `request`, params, body, query string ou variaveis nao validadas | Usar parametros preparados, ORM query builder ou repositories com binding |
| AP-02 | Segredos hardcoded | CRITICAL | `SECRET_KEY`, senhas, tokens, chaves de gateway, SMTP ou credenciais em codigo, config ou resposta HTTP | Mover para variaveis de ambiente e config centralizada; nunca retornar segredo |
| AP-03 | Endpoint administrativo sem protecao | CRITICAL | rotas como `/admin`, reset de banco, query arbitraria, delecao global ou relatorio sensivel sem auth/autorizacao | Exigir autenticacao/autorizacao, remover query arbitraria, registrar auditoria |
| AP-04 | God class / god file / god method | CRITICAL ou HIGH | arquivo/classe com bootstrap, rotas, SQL, validacao, regra de negocio, notificacao e serializacao; tamanho e acoplamento altos | Separar por camadas MVC e por dominio; criar composition root |
| AP-05 | Regra de negocio pesada em route/controller | HIGH | handlers HTTP calculam totais, status, regras de prazo, estoque, pagamento, notificacao ou relatorios complexos | Mover regra para service/use case; manter route fina |
| AP-06 | Persistencia misturada com dominio | HIGH | models/funcoes misturam SQL, regra, serializacao e transacao; controllers importam `db` diretamente | Criar repositories/model methods coesos; controlar transacoes em service |
| AP-07 | Criptografia ou senha insegura | CRITICAL | MD5/SHA1 para senha, base64 como hash, senha em texto puro, tokens fake, comparacao manual sem salt | Usar `werkzeug.security`, `bcrypt`, `argon2`, `crypto.scrypt` ou equivalente |
| AP-08 | Vazamento de dados sensiveis | CRITICAL ou HIGH | serializers retornam senha/hash, healthcheck mostra secret, logs imprimem cartao/chaves/tokens, erros retornam stack/SQL | Redigir dados sensiveis, criar DTOs seguros e logging estruturado |
| AP-09 | N+1 queries / query em loop | MEDIUM ou HIGH | loop sobre entidades executando query por item; relatorios com nested callbacks/queries | Usar join, eager loading, agregacoes ou consultas em lote |
| AP-10 | Estado global mutavel | HIGH ou MEDIUM | cache global, conexao global sem ciclo de vida, variaveis globais de receita/contador, singleton implicito | Injetar dependencias, encapsular cache/conexao e definir ciclo de vida |
| AP-11 | Validacao espalhada e duplicada | MEDIUM | mesmas regras repetidas em endpoints, arrays de status duplicados, validacao manual longa | Extrair schemas/validators e constantes de dominio |
| AP-12 | Error handling inconsistente | MEDIUM | `except:` vazio, retorno de `str(e)` ao cliente, callbacks ignorando `err`, ausencia de rollback | Criar middleware/error handler central e mapear excecoes de dominio |
| AP-13 | APIs deprecated ou legadas | MEDIUM | uso de API documentada como deprecated/legacy na stack detectada | Substituir por equivalente moderno e registrar risco |
| AP-14 | Nomes obscuros e magic values | LOW | variaveis como `u`, `e`, `p`, `cid`, numeros/status soltos, strings repetidas | Renomear para linguagem de dominio e extrair constantes |
| AP-15 | Imports mortos e responsabilidades residuais | LOW | imports nao usados, helpers genericos inchados, comentarios/prints ruidosos | Remover imports mortos e mover utilitarios para modulo coeso |

## APIs Deprecated Ou Legadas

Validar contra a stack detectada e a documentacao local/oficial quando possivel. Exemplos comuns:

- **SQLAlchemy/Flask-SQLAlchemy**: `Model.query.get(id)` e `Query.get()` sao legados no SQLAlchemy 2.x; preferir `db.session.get(Model, id)` quando aplicavel.
- **Python datetime**: `datetime.utcnow()` gera datetime naive e e desencorajado em bases modernas; preferir `datetime.now(timezone.utc)` quando a stack suportar timezone-aware.
- **Node.js Buffer**: `new Buffer()` e deprecated; preferir `Buffer.from`, `Buffer.alloc` ou `Buffer.allocUnsafe` conforme o caso.
- **Node.js crypto**: `crypto.createCipher`/`createDecipher` sao deprecated; preferir `createCipheriv`/`createDecipheriv` com IV explicito.
- **Pacotes abandonados**: `request`, `node-uuid`, `body-parser` desnecessario em Express moderno para JSON simples; confirmar contexto antes de marcar.
- **Framework hooks removidos**: APIs removidas em versoes atuais, como hooks antigos de Flask, devem ser marcadas quando presentes.

Nao marcar uma API como deprecated sem evidencia. Se a versao da dependencia nao estiver clara, registrar como "possivel deprecated" com confianca menor.

## Regras De Evidencia

- Citar arquivo e linha inicial/final.
- Citar o trecho de comportamento em linguagem propria, sem copiar blocos longos.
- Quando o problema for estrutural, citar as principais linhas que demonstram mistura de responsabilidades.
- Nao duplicar findings identicos linha a linha; agrupar ocorrencias quando a causa raiz for a mesma.
- Elevar severidade quando houver input externo, dados sensiveis, operacao destrutiva ou ausencia de autorizacao.
