# Catálogo de Antipadrões

Use este catálogo na Fase 2. Cada achado deve ter evidência concreta, severidade, impacto e recomendação. Classifique pela pior consequência comprovada no contexto.

## Escala de Severidade

- **CRITICAL**: falha grave de segurança ou arquitetura que pode expor dados, permitir execução/consulta indevida, corromper dados ou violar totalmente separação de responsabilidades.
- **HIGH**: forte violação de MVC/SOLID, acoplamento alto ou fragilidade que dificulta manutenção, teste e evolução.
- **MEDIUM**: duplicação, performance ruim, validação incompleta, APIs legadas ou desenho que causa custo moderado.
- **LOW**: legibilidade, nomenclatura, números mágicos, importações mortas e pequenos problemas de organização.

## Antipadrões Obrigatórios

| ID | Antipadrão | Severidade base | Sinais de detecção | Recomendação |
|---|---|---:|---|---|
| AP-01 | Injeção de SQL / consulta dinâmica insegura | CRITICAL | SQL montado por concatenação, string interpolada ou interpolação com `request`, params, body, parâmetros de consulta ou variáveis não validadas | Usar parâmetros preparados, construtor de consultas do ORM ou repositories com vinculação de parâmetros |
| AP-02 | Segredos fixados no código | CRITICAL | `SECRET_KEY`, senhas, tokens, chaves de gateway, SMTP ou credenciais em código, configuração ou resposta HTTP | Mover para variáveis de ambiente e configuração centralizada; nunca retornar segredo |
| AP-03 | Endpoint administrativo sem proteção | CRITICAL | rotas como `/admin`, reset de banco, consulta arbitrária, deleção global ou relatório sensível sem autenticação/autorização | Exigir autenticação/autorização, remover consulta arbitrária, registrar auditoria |
| AP-04 | Classe/arquivo/método Deus | CRITICAL ou HIGH | arquivo/classe com inicialização, rotas, SQL, validação, regra de negócio, notificação e serialização; tamanho e acoplamento altos | Separar por camadas MVC e por domínio; criar raiz de composição |
| AP-05 | Regra de negócio pesada em rota/controller | HIGH | manipuladores HTTP calculam totais, status, regras de prazo, estoque, pagamento, notificação ou relatórios complexos | Mover regra para service/caso de uso; manter rota fina |
| AP-06 | Persistência misturada com domínio | HIGH | models/funções misturam SQL, regra, serialização e transação; controllers importam `db` diretamente | Criar repositories/model methods coesos; controlar transações em service |
| AP-07 | Criptografia ou senha insegura | CRITICAL | MD5/SHA1 para senha, base64 como hash, senha em texto puro, tokens falsos, comparação manual sem salt | Usar `werkzeug.security`, `bcrypt`, `argon2`, `crypto.scrypt` ou equivalente |
| AP-08 | Vazamento de dados sensíveis | CRITICAL ou HIGH | serializadores retornam senha/hash, endpoint de saúde mostra segredo, logs imprimem cartão/chaves/tokens, erros retornam rastreamento de pilha/SQL | Redigir dados sensíveis, criar DTOs seguros e registro de logs estruturado |
| AP-09 | N+1 consultas / consulta em loop | MEDIUM ou HIGH | loop sobre entidades executando consulta por item; relatórios com callbacks/consultas aninhados | Usar joins, eager loading, agregações ou consultas em lote |
| AP-10 | Estado global mutável | HIGH ou MEDIUM | cache global, conexão global sem ciclo de vida, variáveis globais de receita/contador, singleton implícito | Injetar dependências, encapsular cache/conexão e definir ciclo de vida |
| AP-11 | Validação espalhada e duplicada | MEDIUM | mesmas regras repetidas em endpoints, listas de status duplicadas, validação manual longa | Extrair schemas/validators e constantes de domínio |
| AP-12 | Tratamento de erros inconsistente | MEDIUM | `except:` vazio, retorno de `str(e)` ao cliente, callbacks ignorando `err`, ausência de reversão | Criar middleware/tratador de erros central e mapear exceções de domínio |
| AP-13 | APIs obsoletas ou legadas | MEDIUM | uso de API documentada como obsoleta/legada na stack detectada | Substituir por equivalente moderno e registrar risco |
| AP-14 | Nomes obscuros e valores mágicos | LOW | variáveis como `u`, `e`, `p`, `cid`, números/status soltos, strings repetidas | Renomear para linguagem de domínio e extrair constantes |
| AP-15 | Importações mortas e responsabilidades residuais | LOW | imports não usados, helpers genéricos inchados, comentários/prints ruidosos | Remover importações mortas e mover utilitários para módulo coeso |

## APIs Obsoletas ou Legadas

Validar contra a stack detectada e a documentação local/oficial quando possível. Exemplos comuns:

- **SQLAlchemy/Flask-SQLAlchemy**: `Model.query.get(id)` e `Query.get()` são legados no SQLAlchemy 2.x; preferir `db.session.get(Model, id)` quando aplicável.
- **Python datetime**: `datetime.utcnow()` gera datetime sem timezone e é desencorajado em bases modernas; preferir `datetime.now(timezone.utc)` quando a stack suportar timezone explícito.
- **Node.js Buffer**: `new Buffer()` é obsoleto; preferir `Buffer.from`, `Buffer.alloc` ou `Buffer.allocUnsafe` conforme o caso.
- **Node.js crypto**: `crypto.createCipher`/`createDecipher` são obsoletos; preferir `createCipheriv`/`createDecipheriv` com IV explícito.
- **Pacotes abandonados**: `request`, `node-uuid`, `body-parser` desnecessário em Express moderno para JSON simples; confirmar contexto antes de marcar.
- **Hooks de framework removidos**: APIs removidas em versões atuais, como hooks antigos de Flask, devem ser marcadas quando presentes.

Não marcar uma API como obsoleta sem evidência. Se a versão da dependência não estiver clara, registrar como "possivelmente obsoleta" com confiança menor.

## Regras de Evidência

- Citar arquivo e linha inicial/final.
- Citar o trecho de comportamento em linguagem própria, sem copiar blocos longos.
- Quando o problema for estrutural, citar as principais linhas que demonstram mistura de responsabilidades.
- Não duplicar achados idênticos linha a linha; agrupar ocorrências quando a causa raiz for a mesma.
- Elevar severidade quando houver entrada externa, dados sensíveis, operação destrutiva ou ausência de autorização.
