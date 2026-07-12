#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$SCRIPT_DIR/env.list}"

if [[ ! -f "$ENV_FILE" ]]; then
  printf 'ERRO: arquivo de configuracao nao encontrado: %s\n' "$ENV_FILE" >&2
  exit 1
fi

# shellcheck source=/dev/null
set -a
source "$ENV_FILE"
set +a

BASE_URL="${BASE_URL:-http://localhost:5000}"
BASE_URL="${BASE_URL%/}"
CURL_CONNECT_TIMEOUT="${CURL_CONNECT_TIMEOUT:-5}"
CURL_MAX_TIME="${CURL_MAX_TIME:-30}"
ADMIN_EMAIL="${ADMIN_EMAIL:-${SEED_ADMIN_EMAIL:-}}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-${SEED_ADMIN_PASSWORD:-}}"
CLIENT_NAME="${CLIENT_NAME:-Cliente teste pos-refactor}"
CLIENT_EMAIL="${CLIENT_EMAIL:-cliente.pos.refactor@example.com}"
CLIENT_PASSWORD="${CLIENT_PASSWORD:-cliente123}"
ADMIN_TOKEN="${ADMIN_TOKEN:-}"
TEST_RESET_DB="${TEST_RESET_DB:-false}"
VERBOSE="${VERBOSE:-false}"

for command_name in curl python3; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'ERRO: comando obrigatorio nao encontrado: %s\n' "$command_name" >&2
    exit 1
  fi
done

if [[ -z "$ADMIN_EMAIL" || -z "$ADMIN_PASSWORD" ]]; then
  printf 'ERRO: defina ADMIN_EMAIL e ADMIN_PASSWORD em %s\n' "$ENV_FILE" >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
ADMIN_COOKIE_JAR="$TMP_DIR/admin.cookies"
CLIENT_COOKIE_JAR="$TMP_DIR/client.cookies"
RESPONSE_FILE="$TMP_DIR/response.json"
PASSED=0
LAST_BODY=''

cleanup() {
  rm -rf -- "$TMP_DIR"
}
trap cleanup EXIT

is_true() {
  case "${1,,}" in
    1|true|yes|on) return 0 ;;
    *) return 1 ;;
  esac
}

status_is_expected() {
  local actual="$1"
  local expected_csv="$2"
  local expected
  local -a expected_statuses

  IFS=',' read -r -a expected_statuses <<< "$expected_csv"
  for expected in "${expected_statuses[@]}"; do
    if [[ "$actual" == "$expected" ]]; then
      return 0
    fi
  done
  return 1
}

request() {
  local label="$1"
  local method="$2"
  local path="$3"
  local expected_statuses="$4"
  local status
  shift 4

  if ! status="$(curl \
    --silent \
    --show-error \
    --connect-timeout "$CURL_CONNECT_TIMEOUT" \
    --max-time "$CURL_MAX_TIME" \
    --request "$method" \
    --url "$BASE_URL$path" \
    --header 'Accept: application/json' \
    --output "$RESPONSE_FILE" \
    --write-out '%{http_code}' \
    "$@")"; then
    printf 'FALHA: %s - nao foi possivel acessar %s%s\n' "$label" "$BASE_URL" "$path" >&2
    exit 1
  fi

  LAST_BODY="$(<"$RESPONSE_FILE")"

  if ! status_is_expected "$status" "$expected_statuses"; then
    printf 'FALHA: %s - esperado HTTP %s, recebido HTTP %s\n' \
      "$label" "$expected_statuses" "$status" >&2
    printf 'Resposta: %s\n' "$LAST_BODY" >&2
    exit 1
  fi

  PASSED=$((PASSED + 1))
  printf '[OK] %-46s HTTP %s\n' "$label" "$status"
  if is_true "$VERBOSE"; then
    python3 -m json.tool "$RESPONSE_FILE" 2>/dev/null || printf '%s\n' "$LAST_BODY"
  fi
}

json_get() {
  local path="$1"

  python3 -c '
import json
import sys

value = json.load(sys.stdin)
for key in sys.argv[1].split("."):
    value = value[key]
print(value)
' "$path" <<< "$LAST_BODY"
}

credentials_payload() {
  python3 -c '
import json
import sys

print(json.dumps({"email": sys.argv[1], "senha": sys.argv[2]}))
' "$1" "$2"
}

client_payload() {
  python3 -c '
import json
import sys

print(json.dumps({"nome": sys.argv[1], "email": sys.argv[2], "senha": sys.argv[3]}))
' "$CLIENT_NAME" "$CLIENT_EMAIL" "$CLIENT_PASSWORD"
}

product_payload() {
  python3 -c '
import json
import sys

print(json.dumps({
    "nome": sys.argv[1],
    "descricao": sys.argv[2],
    "preco": float(sys.argv[3]),
    "estoque": int(sys.argv[4]),
    "categoria": sys.argv[5],
}))
' "$@"
}

order_payload() {
  python3 -c '
import json
import sys

print(json.dumps({
    "usuario_id": int(sys.argv[1]),
    "itens": [{"produto_id": int(sys.argv[2]), "quantidade": 1}],
}))
' "$1" "$2"
}

RUN_ID="$(date +%s)-$$"
PRODUCT_NAME="Produto curl pos-refactor $RUN_ID"

printf 'Testando API em %s\n' "$BASE_URL"
printf 'Configuracao carregada de %s\n\n' "$ENV_FILE"

# Endpoints publicos.
request 'GET /' GET / 200
request 'GET /health' GET /health 200
request 'GET /produtos' GET /produtos 200

# Cria ou reutiliza um cliente e guarda sua sessao em cookie separado.
request 'POST /usuarios (cliente)' POST /usuarios '201,409' \
  --header 'Content-Type: application/json' \
  --data "$(client_payload)"

request 'POST /login (cliente)' POST /login 200 \
  --header 'Content-Type: application/json' \
  --cookie-jar "$CLIENT_COOKIE_JAR" \
  --data "$(credentials_payload "$CLIENT_EMAIL" "$CLIENT_PASSWORD")"
CLIENT_ID="$(json_get 'dados.id')"

request 'GET /usuarios/<id> (proprio cliente)' GET "/usuarios/$CLIENT_ID" 200 \
  --cookie "$CLIENT_COOKIE_JAR"

# Login administrativo: o cookie retornado autentica as rotas de administracao.
request 'POST /login (admin)' POST /login 200 \
  --header 'Content-Type: application/json' \
  --cookie-jar "$ADMIN_COOKIE_JAR" \
  --data "$(credentials_payload "$ADMIN_EMAIL" "$ADMIN_PASSWORD")"

request 'GET /usuarios (admin)' GET /usuarios 200 \
  --cookie "$ADMIN_COOKIE_JAR"

# O produto criado torna os testes independentes dos IDs e do estoque do seed.
request 'POST /produtos (admin)' POST /produtos 201 \
  --header 'Content-Type: application/json' \
  --cookie "$ADMIN_COOKIE_JAR" \
  --data "$(product_payload "$PRODUCT_NAME" 'Criado pelo teste curl' 25.50 5 geral)"
PRODUCT_ID="$(json_get 'dados.id')"

request 'GET /produtos/<id>' GET "/produtos/$PRODUCT_ID" 200

request 'PUT /produtos/<id> (admin)' PUT "/produtos/$PRODUCT_ID" 200 \
  --header 'Content-Type: application/json' \
  --cookie "$ADMIN_COOKIE_JAR" \
  --data "$(product_payload "$PRODUCT_NAME atualizado" 'Atualizado pelo teste curl' 30.75 8 livros)"

request 'GET /produtos/busca' GET /produtos/busca 200 \
  --get \
  --data-urlencode "q=$PRODUCT_NAME" \
  --data-urlencode 'categoria=livros' \
  --data-urlencode 'preco_min=1' \
  --data-urlencode 'preco_max=100'

# Cliente autenticado cria e consulta apenas o proprio pedido.
request 'POST /pedidos (cliente)' POST /pedidos 201 \
  --header 'Content-Type: application/json' \
  --cookie "$CLIENT_COOKIE_JAR" \
  --data "$(order_payload "$CLIENT_ID" "$PRODUCT_ID")"
ORDER_ID="$(json_get 'dados.pedido_id')"

request 'GET /pedidos/usuario/<id> (cliente)' GET "/pedidos/usuario/$CLIENT_ID" 200 \
  --cookie "$CLIENT_COOKIE_JAR"

# Endpoints que exigem papel administrativo.
request 'GET /pedidos (admin)' GET /pedidos 200 \
  --cookie "$ADMIN_COOKIE_JAR"

request 'PUT /pedidos/<id>/status (admin)' PUT "/pedidos/$ORDER_ID/status" 200 \
  --header 'Content-Type: application/json' \
  --cookie "$ADMIN_COOKIE_JAR" \
  --data '{"status":"aprovado"}'

request 'GET /relatorios/vendas (admin)' GET /relatorios/vendas 200 \
  --cookie "$ADMIN_COOKIE_JAR"

request 'DELETE /produtos/<id> (admin)' DELETE "/produtos/$PRODUCT_ID" 200 \
  --cookie "$ADMIN_COOKIE_JAR"

# Mantido por compatibilidade, mas deve sempre recusar SQL arbitrario.
request 'POST /admin/query (bloqueado por contrato)' POST /admin/query 403 \
  --header 'Content-Type: application/json' \
  --cookie "$ADMIN_COOKIE_JAR" \
  --data '{"sql":"SELECT COUNT(*) AS total FROM produtos"}'

# O reset real e destrutivo e, por isso, so roda quando explicitamente habilitado.
if is_true "$TEST_RESET_DB"; then
  if [[ -z "$ADMIN_TOKEN" ]]; then
    printf 'ERRO: TEST_RESET_DB=true exige ADMIN_TOKEN em %s\n' "$ENV_FILE" >&2
    exit 1
  fi
  request 'POST /admin/reset-db (reset destrutivo)' POST /admin/reset-db 200 \
    --header "X-Admin-Token: $ADMIN_TOKEN"
else
  request 'POST /admin/reset-db (protecao validada)' POST /admin/reset-db 403
fi

printf '\nSucesso: %d chamadas validadas; todos os endpoints foram exercitados.\n' "$PASSED"
