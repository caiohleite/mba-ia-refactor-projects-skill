#!/usr/bin/env bash

BASE_URL="${BASE_URL:-http://localhost:5000}"

curl "$BASE_URL/"

curl "$BASE_URL/produtos"
curl "$BASE_URL/produtos/busca?q=Notebook&categoria=informatica&preco_min=100&preco_max=7000"
curl "$BASE_URL/produtos/1"
curl -X POST "$BASE_URL/produtos" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Produto via curl","descricao":"Produto de teste","preco":25.50,"estoque":4,"categoria":"geral"}'
curl -X PUT "$BASE_URL/produtos/1" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Notebook Gamer","descricao":"Notebook atualizado via curl","preco":5999.99,"estoque":10,"categoria":"informatica"}'
curl -X DELETE "$BASE_URL/produtos/2"

curl "$BASE_URL/usuarios"
curl "$BASE_URL/usuarios/1"
curl -X POST "$BASE_URL/usuarios" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Usuario Curl","email":"curl@example.com","senha":"segredo"}'
curl -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@loja.com","senha":"admin123"}'

curl -X POST "$BASE_URL/pedidos" \
  -H "Content-Type: application/json" \
  -d '{"usuario_id":1,"itens":[{"produto_id":1,"quantidade":1}]}'
curl "$BASE_URL/pedidos"
curl "$BASE_URL/pedidos/usuario/1"
curl -X PUT "$BASE_URL/pedidos/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status":"aprovado"}'

curl "$BASE_URL/relatorios/vendas"
curl "$BASE_URL/health"

curl -X POST "$BASE_URL/admin/query" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT COUNT(*) AS total FROM produtos"}'
#curl -X POST "$BASE_URL/admin/reset-db"
