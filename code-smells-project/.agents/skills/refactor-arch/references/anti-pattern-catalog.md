# Catálogo de Anti-Patterns

Use este catálogo na Fase 2. Cada achado deve ter evidência concreta, severidade, impacto e recomendação. Classifique pela pior consequência comprovada no contexto.

## Escala de Severidade

- **CRITICAL**: falha grave de segurança ou arquitetura que pode expor dados, permitir execução/consulta indevida, corromper dados ou violar totalmente separação de responsabilidades.
- **HIGH**: forte violação de MVC/SOLID, acoplamento alto ou fragilidade que dificulta manutenção, teste e evolução.
- **MEDIUM**: duplicação, performance ruim, validação incompleta, APIs legadas ou desenho que causa custo moderado.
- **LOW**: legibilidade, nomenclatura, magic numbers, imports mortos e pequenos problemas de organização.

## Anti-Patterns Obrigatórios

| ID | Anti-pattern | Severidade base | Sinais de detecção | Recomendação |
|---|---|---:|---|---|
| AP-01 | SQL Injection / query dinâmica insegura | CRITICAL | SQL montado por concatenação, template string ou interpolação com `request`, params, body, query string ou variáveis não validadas | Usar parâmetros preparados, ORM query builder ou repositories com binding |
| AP-02 | Segredos hardcoded | CRITICAL | `SECRET_KEY`, senhas, tokens, chaves de gateway, SMTP ou credenciais em código, config ou resposta HTTP | Mover para variáveis de ambiente e config centralizada; nunca retornar segredo |
| AP-03 | Endpoint administrativo sem proteção | CRITICAL | rotas como `/admin`, reset de banco, query arbitrária, deleção global ou relatório sensível sem auth/autorização | Exigir autenticação/autorização, remover query arbitrária, registrar auditoria |
| AP-04 | God class / god file / god method | CRITICAL ou HIGH | arquivo/classe com bootstrap, rotas, SQL, validação, regra de negócio, notificação e serialização; tamanho e acoplamento altos | Separar por camadas MVC e por domínio; criar composition root |
| AP-05 | Regra de negócio pesada em route/controller | HIGH | handlers HTTP calculam totais, status, regras de prazo, estoque, pagamento, notificação ou relatórios complexos | Mover regra para service/use case; manter route fina |
| AP-06 | Persistência misturada com domínio | HIGH | models/funções misturam SQL, regra, serialização e transação; controllers importam `db` diretamente | Criar repositories/model methods coesos; controlar transações em service |
| AP-07 | Criptografia ou senha insegura | CRITICAL | MD5/SHA1 para senha, base64 como hash, senha em texto puro, tokens fake, comparação manual sem salt | Usar `werkzeug.security`, `bcrypt`, `argon2`, `crypto.scrypt` ou equivalente |
| AP-08 | Vazamento de dados sensíveis | CRITICAL ou HIGH | serializers retornam senha/hash, healthcheck mostra secret, logs imprimem cartão/chaves/tokens, erros retornam stack/SQL | Redigir dados sensíveis, criar DTOs seguros e logging estruturado |
| AP-09 | N+1 queries / query em loop | MEDIUM ou HIGH | loop sobre entidades executando query por item; relatórios com nested callbacks/queries | Usar join, eager loading, agregações ou consultas em lote |
| AP-10 | Estado global mutável | HIGH ou MEDIUM | cache global, conexão global sem ciclo de vida, variáveis globais de receita/contador, singleton implícito | Injetar dependências, encapsular cache/conexão e definir ciclo de vida |
| AP-11 | Validação espalhada e duplicada | MEDIUM | mesmas regras repetidas em endpoints, arrays de status duplicados, validação manual longa | Extrair schemas/validators e constantes de domínio |
| AP-12 | Error handling inconsistente | MEDIUM | `except:` vazio, retorno de `str(e)` ao cliente, callbacks ignorando `err`, ausência de rollback | Criar middleware/error handler central e mapear exceções de domínio |
| AP-13 | APIs obsoletas ou legadas | MEDIUM | uso de API documentada como deprecated/legacy na stack detectada | Substituir por equivalente moderno e registrar risco |
| AP-14 | Nomes obscuros e magic values | LOW | variáveis como `u`, `e`, `p`, `cid`, números/status soltos, strings repetidas | Renomear para linguagem de domínio e extrair constantes |
| AP-15 | Imports mortos e responsabilidades residuais | LOW | imports não usados, helpers genéricos inchados, comentários/prints ruidosos | Remover imports mortos e mover utilitários para módulo coeso |

## APIs Obsoletas ou Legadas

Validar contra a stack detectada e a documentação local/oficial quando possível. Exemplos comuns:

- **SQLAlchemy/Flask-SQLAlchemy**: `Model.query.get(id)` e `Query.get()` são legados no SQLAlchemy 2.x; preferir `db.session.get(Model, id)` quando aplicável.
- **Python datetime**: `datetime.utcnow()` gera datetime naive e é desencorajado em bases modernas; preferir `datetime.now(timezone.utc)` quando a stack suportar timezone-aware.
- **Node.js Buffer**: `new Buffer()` é deprecated; preferir `Buffer.from`, `Buffer.alloc` ou `Buffer.allocUnsafe` conforme o caso.
- **Node.js crypto**: `crypto.createCipher`/`createDecipher` são deprecated; preferir `createCipheriv`/`createDecipheriv` com IV explícito.
- **Pacotes abandonados**: `request`, `node-uuid`, `body-parser` desnecessário em Express moderno para JSON simples; confirmar contexto antes de marcar.
- **Framework hooks removidos**: APIs removidas em versões atuais, como hooks antigos de Flask, devem ser marcadas quando presentes.

Não marcar uma API como deprecated sem evidência. Se a versão da dependência não estiver clara, registrar como "possível deprecated" com confiança menor.

## Regras de Evidência

- Citar arquivo e linha inicial/final.
- Citar o trecho de comportamento em linguagem própria, sem copiar blocos longos.
- Quando o problema for estrutural, citar as principais linhas que demonstram mistura de responsabilidades.
- Não duplicar achados idênticos linha a linha; agrupar ocorrências quando a causa raiz for a mesma.
- Elevar severidade quando houver input externo, dados sensíveis, operação destrutiva ou ausência de autorização.
