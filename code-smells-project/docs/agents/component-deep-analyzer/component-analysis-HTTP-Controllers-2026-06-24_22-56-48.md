# Component Deep Analysis Report

**Component**: HTTP Controllers

**Generated on**: 2026-06-24 22:56:48

## Executive Summary

The HTTP Controllers component is implemented in `controllers.py`. It translates Flask requests into calls to `models.py`, performs validation for products, users, orders, and status transitions, and serializes JSON responses.

This component contains significant business validation logic and error handling. It also returns exception messages to clients in many branches and exposes sensitive operational information through the health check response at `controllers.py:276-290`.

## Data Flow Analysis

Request data enters through `request.get_json()` or `request.args`, is validated in controller functions, then passed to model functions. Model return values are wrapped in JSON envelopes such as `{"dados": ..., "sucesso": True}`. Exceptions are generally caught and returned as HTTP 500 responses.

## Overview of the business rules

| Rule Type | Rule Description | Location |
|-----------|------------------|----------|
| Product required fields | Product creation/update requires `nome`, `preco`, and `estoque`. | `controllers.py:28-35`, `controllers.py:72-79` |
| Product value constraints | Product price and stock cannot be negative. | `controllers.py:43-46`, `controllers.py:87-90` |
| Product name constraints | Product name length must be between 2 and 200 for creation. | `controllers.py:47-50` |
| Product category whitelist | Category must be one of six hardcoded categories on creation. | `controllers.py:52-54` |
| User creation required fields | `nome`, `email`, and `senha` are required. | `controllers.py:153-159` |
| Login required fields | `email` and `senha` are required. | `controllers.py:169-174` |
| Order required fields | `usuario_id` and at least one item are required. | `controllers.py:195-201` |
| Order status whitelist | Status must be one of `pendente`, `aprovado`, `enviado`, `entregue`, or `cancelado`. | `controllers.py:240-243` |

## Detailed breakdown of the business rules

### Business Rule: Product Validation

**Overview**:
Product creation and update requests are validated before persistence calls.

**Detailed description**:
Creation requires a JSON body and the fields `nome`, `preco`, and `estoque`. Optional fields include `descricao` and `categoria`, with default category `geral`.

For creation, price and stock cannot be negative. The product name must be at least two characters and no longer than 200 characters. The creation flow also validates category membership against a hardcoded list.

The update flow validates existence before body validation and enforces required fields, non-negative price, and non-negative stock. It does not repeat the creation name length or category whitelist checks in the inspected code.

**Rule workflow**:
Read JSON -> validate required fields -> derive optional values -> validate constraints -> call model -> return JSON response.

### Business Rule: Order Creation Request Validation

**Overview**:
Order creation requires a user id and at least one item.

**Detailed description**:
The controller rejects missing JSON bodies, missing `usuario_id`, and empty `itens`. It delegates inventory checks, price calculation, order insertion, and stock decrement to `models.criar_pedido`.

If the model returns a dictionary containing `erro`, the controller returns HTTP 400. On success, it prints simulated notifications for email, SMS, and push.

The controller does not validate item schema beyond passing the list to the model. Required keys such as `produto_id` and `quantidade` are implied by model usage.

**Rule workflow**:
Read JSON -> validate `usuario_id` and `itens` -> call model -> emit console notifications -> return created response.

## Component Structure

| File | Responsibility |
|------|----------------|
| `controllers.py` | Product, user, login, order, report, and health HTTP handlers. |

## Dependency Analysis

- Internal dependencies: `models`, `database.get_db`.
- External dependencies: Flask `request` and `jsonify`.

## Afferent and Efferent Coupling

| Component | Afferent Coupling | Efferent Coupling | Critical |
|-----------|-------------------|-------------------|----------|
| `controllers.py` | 1 (`app.py`) | 3 (`flask`, `models`, `database`) | Yes |
| Product handlers | 6 routes | `models` product functions | Yes |
| User/login handlers | 4 routes | `models` user functions | Yes |
| Order handlers | 4 routes | `models` order functions | Yes |
| Report/health handlers | 2 routes | `models`, `get_db` | Medium |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| Product endpoints | GET, POST, PUT, DELETE | Product CRUD and search. |
| User endpoints | GET, POST | User listing, lookup, and creation. |
| `/login` | POST | Plain credential login flow. |
| Order endpoints | GET, POST, PUT | Order creation, listing, user listing, and status updates. |
| `/relatorios/vendas` | GET | Sales aggregates. |
| `/health` | GET | Database check and counts. |

## Integration Points

| Integration | Type | Purpose | Protocol | Data Format | Error Handling |
|-------------|------|---------|----------|-------------|----------------|
| Flask request/response | Framework API | Read inputs and return JSON | HTTP | JSON/query string | Broad `except Exception` handlers. |
| Models module | Internal API | Business and persistence operations | In-process call | Python dict/list | Model errors are returned or converted to 500. |
| SQLite via `get_db` | Database | Health check counts | In-process file DB | SQL rows | Exceptions returned as health error details. |

## Design Patterns & Architecture

| Pattern | Implementation | Location | Purpose |
|---------|----------------|----------|---------|
| Controller layer | Procedural request handlers. | `controllers.py` | Request validation and response formatting. |
| Service logic in controller | Validation and notification side effects live in handlers. | `controllers.py:24-255` | Implements workflow logic near HTTP boundary. |

## Technical Debt & Risks

| Risk Level | Component Area | Issue | Impact |
|------------|----------------|-------|--------|
| High | Health check | Returns debug flag, DB path, and secret key. | Sensitive operational data exposure. |
| Medium | Error handling | Returns `str(e)` to clients in many handlers. | Internal error disclosure. |
| Medium | Validation | Product update validation differs from creation validation. | Inconsistent domain constraints. |
| Medium | Order handling | Item schema is not checked in controller. | Runtime exceptions for malformed items. |

## Test Coverage Analysis

| Component | Unit Tests | Integration Tests | Coverage | Test Quality |
|-----------|------------|-------------------|----------|--------------|
| HTTP Controllers | Not found | Not found | No tests found in scope | No test files or test framework configuration were found. |
