# Playbook De Refatoracao

Use este playbook na Fase 3. Aplique somente os padroes relacionados aos findings aprovados. Os exemplos sao ilustrativos; adapte nomes e idioms a stack atual.

## 1. Extrair Configuracao E Segredos

**Antes**

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.run(debug=True)
```

**Depois**

```python
import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
```

Regra: substituir valores sensiveis por variaveis de ambiente e defaults seguros para desenvolvimento. Nunca retornar segredos em healthcheck.

## 2. Trocar SQL Concatenado Por Parametros

**Antes**

```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "'")
```

**Depois**

```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

Regra: toda entrada externa deve passar por binding de parametros, ORM seguro ou query builder.

## 3. Afinar Routes E Controllers

**Antes**

```javascript
app.post('/api/checkout', (req, res) => {
  // valida, consulta banco, processa pagamento, matricula e responde
});
```

**Depois**

```javascript
router.post('/api/checkout', checkoutController.create);

async function create(req, res, next) {
  try {
    const result = await checkoutService.checkout(req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}
```

Regra: route registra endpoint; controller adapta HTTP; service executa caso de uso.

## 4. Dividir God Object Por Dominio

**Antes**

```javascript
class AppManager {
  initDb() {}
  setupRoutes(app) {}
  checkout() {}
  financialReport() {}
}
```

**Depois**

```text
db/connection.js
routes/checkoutRoutes.js
controllers/checkoutController.js
services/checkoutService.js
repositories/courseRepository.js
repositories/paymentRepository.js
```

Regra: separar bootstrap, rotas, controllers, services e repositories. Mover um dominio por vez.

## 5. Remover N+1 Queries

**Antes**

```python
for task in tasks:
    user = User.query.get(task.user_id)
    category = Category.query.get(task.category_id)
```

**Depois**

```python
tasks = (
    Task.query
    .options(db.joinedload(Task.user), db.joinedload(Task.category))
    .all()
)
```

Regra: usar eager loading, joins, agregacoes ou consultas em lote. Em SQL direto, buscar mapas por IDs antes do loop.

## 6. Substituir Criptografia Fraca

**Antes**

```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

**Depois**

```python
from werkzeug.security import generate_password_hash, check_password_hash

self.password = generate_password_hash(pwd)
```

Regra: usar algoritmo com salt e custo configuravel. Para Node.js, preferir `bcrypt` ou `crypto.scrypt` com salt.

## 7. Criar DTO Seguro

**Antes**

```python
def to_dict(self):
    return {"email": self.email, "password": self.password}
```

**Depois**

```python
def to_public_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email}
```

Regra: separar representacao interna de resposta publica. Nunca serializar senha, token, cartao ou segredo.

## 8. Centralizar Error Handling

**Antes**

```python
try:
    service.execute()
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

**Depois**

```python
@app.errorhandler(DomainError)
def handle_domain_error(error):
    return jsonify({"error": error.message}), error.status_code
```

Regra: mapear erros de dominio e infraestrutura em um lugar. Evitar vazar detalhes internos.

## 9. Extrair Validacao Reutilizavel

**Antes**

```python
if status not in ["pending", "in_progress", "done", "cancelled"]:
    return jsonify({"error": "Status invalido"}), 400
```

**Depois**

```python
VALID_STATUSES = {"pending", "in_progress", "done", "cancelled"}

def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValidationError("Status invalido")
```

Regra: validacoes repetidas pertencem a validators, schemas ou objetos de dominio.

## 10. Modernizar APIs Deprecated

**Antes**

```python
user = User.query.get(user_id)
```

**Depois**

```python
user = db.session.get(User, user_id)
```

Regra: trocar APIs deprecated quando a versao da stack confirmar suporte ao equivalente moderno. Se a troca afetar muitos pontos, aplicar em etapa isolada e validar.

## Ordem Recomendada

1. Criar config e error handling.
2. Extrair repositories/model access sem mudar contrato.
3. Extrair services com regras de negocio.
4. Afinar controllers e routes.
5. Corrigir seguranca critica.
6. Otimizar N+1 e duplicacoes.
7. Modernizar deprecated APIs.
8. Rodar validacao completa.

## Mapeamento De Anti-Patterns Para Transformacoes

Use esta tabela para montar a matriz de cobertura do plano:

| Anti-pattern | Padroes principais | Observacoes |
|---|---|---|
| AP-01 SQL Injection | 2, 4 | Corrigir antes de mover grandes blocos quando houver input externo ativo |
| AP-02 Segredos hardcoded | 1, 7 | Remover de codigo, respostas e logs |
| AP-03 Endpoint administrativo sem protecao | 3, 8 | Exigir auth/autorizacao ou remover recurso perigoso com aprovacao |
| AP-04 God class/file/method | 3, 4, 8 | Dividir por dominio e por camada |
| AP-05 Regra pesada em route/controller | 3, 4, 9 | Extrair use cases/services e validadores |
| AP-06 Persistencia misturada com dominio | 2, 4 | Introduzir repositories/data access e transacoes explicitas |
| AP-07 Criptografia/senha insegura | 6, 7 | Migrar hash e DTO com cuidado para nao quebrar login |
| AP-08 Vazamento de dados sensiveis | 1, 7, 8 | Criar DTO publico e sanitizar logs/erros |
| AP-09 N+1 queries | 5 | Trocar loops com query por join/eager loading/lote |
| AP-10 Estado global mutavel | 1, 4 | Encapsular ciclo de vida e injetar dependencias |
| AP-11 Validacao espalhada | 9 | Centralizar constantes, schemas ou validadores |
| AP-12 Error handling inconsistente | 8 | Mapear erros de dominio e infraestrutura |
| AP-13 APIs deprecated | 10 | Modernizar em etapa isolada e validar versao da stack |
| AP-14 Nomes obscuros/magic values | 9 | Corrigir junto da camada tocada, evitando refactor cosmetico amplo |
| AP-15 Imports mortos/residuos | 8, 9 | Limpar no final para reduzir risco |
