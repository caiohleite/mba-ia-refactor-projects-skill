# Guia de Refatoração

Use este guia na Fase 3. Aplique somente os padrões relacionados aos achados aprovados. Os exemplos são ilustrativos; adapte nomes e padrões idiomáticos à stack atual.

## 1. Extrair Configuração e Segredos

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

Regra: substituir valores sensíveis por variáveis de ambiente e valores padrão seguros para desenvolvimento. Nunca retornar segredos em endpoints de saúde.

## 2. Trocar SQL Concatenado por Parâmetros

**Antes**

```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "'")
```

**Depois**

```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

Regra: toda entrada externa deve passar por vinculação de parâmetros, ORM seguro ou construtor de consultas.

## 3. Afinar Rotas e Controllers

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

Regra: a rota registra endpoint; o controller adapta HTTP; o service executa o caso de uso.

## 4. Dividir Objeto Deus por Domínio

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

Regra: separar inicialização, rotas, controllers, services e repositories. Mover um domínio por vez.

## 5. Remover N+1 Consultas

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

Regra: usar eager loading, joins, agregações ou consultas em lote. Em SQL direto, buscar mapas por IDs antes do loop.

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

Regra: usar algoritmo com salt e custo configurável. Para Node.js, preferir `bcrypt` ou `crypto.scrypt` com salt.

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

Regra: separar representação interna de resposta pública. Nunca serializar senha, token, cartão ou segredo.

## 8. Centralizar Tratamento de Erros

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

Regra: mapear erros de domínio e infraestrutura em um lugar. Evitar vazar detalhes internos.

## 9. Extrair Validação Reutilizável

**Antes**

```python
if status not in ["pending", "in_progress", "done", "cancelled"]:
    return jsonify({"error": "Status inválido"}), 400
```

**Depois**

```python
VALID_STATUSES = {"pending", "in_progress", "done", "cancelled"}

def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValidationError("Status inválido")
```

Regra: validações repetidas pertencem a validadores, schemas ou objetos de domínio.

## 10. Modernizar APIs Obsoletas

**Antes**

```python
user = User.query.get(user_id)
```

**Depois**

```python
user = db.session.get(User, user_id)
```

Regra: trocar APIs obsoletas quando a versão da stack confirmar suporte ao equivalente moderno. Se a troca afetar muitos pontos, aplicar em etapa isolada e validar.

## Ordem Recomendada

1. Criar configuração e tratamento de erros.
2. Extrair repositories/acesso a models sem mudar contrato.
3. Extrair services com regras de negócio.
4. Afinar controllers e rotas.
5. Corrigir segurança crítica.
6. Otimizar N+1 e duplicações.
7. Modernizar APIs obsoletas.
8. Rodar validação completa.

## Mapeamento de Antipadrões para Transformações

Use esta tabela para montar a matriz de cobertura do plano:

| Antipadrão | Padrões principais | Observações |
|---|---|---|
| AP-01 Injeção de SQL | 2, 4 | Corrigir antes de mover grandes blocos quando houver entrada externa ativa |
| AP-02 Segredos fixados no código | 1, 7 | Remover de código, respostas e logs |
| AP-03 Endpoint administrativo sem proteção | 3, 8 | Exigir autenticação/autorização ou remover recurso perigoso com aprovação |
| AP-04 Classe/arquivo/método Deus | 3, 4, 8 | Dividir por domínio e por camada |
| AP-05 Regra pesada em rota/controller | 3, 4, 9 | Extrair casos de uso/services e validadores |
| AP-06 Persistência misturada com domínio | 2, 4 | Introduzir repositories/acesso a dados e transações explícitas |
| AP-07 Criptografia/senha insegura | 6, 7 | Migrar hash e DTO com cuidado para não quebrar login |
| AP-08 Vazamento de dados sensíveis | 1, 7, 8 | Criar DTO público e sanitizar logs/erros |
| AP-09 N+1 consultas | 5 | Trocar loops com consulta por join/eager loading/lote |
| AP-10 Estado global mutável | 1, 4 | Encapsular ciclo de vida e injetar dependências |
| AP-11 Validação espalhada | 9 | Centralizar constantes, schemas ou validadores |
| AP-12 Tratamento de erros inconsistente | 8 | Mapear erros de domínio e infraestrutura |
| AP-13 APIs obsoletas | 10 | Modernizar em etapa isolada e validar versão da stack |
| AP-14 Nomes obscuros/valores mágicos | 9 | Corrigir junto da camada tocada, evitando refatoração cosmética ampla |
| AP-15 Importações mortas/resíduos | 8, 9 | Limpar no final para reduzir risco |
