# Component Deep Analysis Report

**Component**: Administrative Operations

**Generated on**: 2026-06-24 22:56:48

## Executive Summary

Administrative Operations are implemented as two Flask routes in `app.py:47-78`: `/admin/reset-db` and `/admin/query`. They directly use the database connection and bypass the controller/model layer.

This is the highest-risk component in the application because it exposes destructive database reset and arbitrary SQL execution behavior through HTTP routes without visible authentication or authorization checks in the inspected code.

## Data Flow Analysis

For reset, an HTTP POST invokes `reset_database()`, which deletes data from four tables and commits. For query execution, POST JSON is parsed, the `sql` value is passed to `cursor.execute`, and either selected rows or a commit confirmation is returned.

## Overview of the business rules

| Rule Type | Rule Description | Location |
|-----------|------------------|----------|
| Reset order | Delete order items, orders, products, and users in that order. | `app.py:51-54` |
| Reset commit | Commit reset after all delete statements. | `app.py:55` |
| SQL required | Empty `sql` payload is rejected. | `app.py:61-64` |
| SELECT response | SQL beginning with `SELECT` returns fetched rows. | `app.py:69-73` |
| Mutation response | Non-SELECT SQL is committed and returns success message. | `app.py:74-76` |

## Detailed breakdown of the business rules

### Business Rule: Database Reset

**Overview**:
The reset endpoint deletes all rows from application tables.

**Detailed description**:
The function obtains the shared database connection, creates a cursor, and executes four delete statements. It deletes `itens_pedido` before `pedidos`, then deletes `produtos`, then `usuarios`.

After deletion, it commits the transaction and logs a reset message to stdout. The endpoint returns a JSON success message with HTTP 200.

No authentication, authorization, confirmation token, environment check, or request body validation is visible in this function.

**Rule workflow**:
POST `/admin/reset-db` -> get DB -> delete rows -> commit -> return success.

### Business Rule: Arbitrary SQL Execution

**Overview**:
The query endpoint executes client-submitted SQL.

**Detailed description**:
The function reads JSON and extracts the `sql` key. Missing or empty SQL receives HTTP 400.

The provided SQL text is executed directly. Queries starting with `SELECT` return fetched rows converted to dictionaries. Other statements are committed.

The function catches any exception and returns its message as the HTTP 500 response body. This exposes database error details to callers.

**Rule workflow**:
POST `/admin/query` -> parse `sql` -> execute -> fetch rows or commit -> return result or error.

## Component Structure

| File | Responsibility |
|------|----------------|
| `app.py:47-78` | Admin reset and SQL execution endpoints. |

## Dependency Analysis

- Internal dependencies: `database.get_db`.
- External dependencies: Flask `request`, `jsonify`.
- Data dependency: all SQLite application tables.

## Afferent and Efferent Coupling

| Component | Afferent Coupling | Efferent Coupling | Critical |
|-----------|-------------------|-------------------|----------|
| `reset_database()` | 1 route | `get_db`, SQLite tables | Yes |
| `executar_query()` | 1 route | Flask request, `get_db`, arbitrary SQL | Yes |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/reset-db` | POST | Deletes rows from core database tables. |
| `/admin/query` | POST | Executes SQL provided in JSON payload. |

## Integration Points

| Integration | Type | Purpose | Protocol | Data Format | Error Handling |
|-------------|------|---------|----------|-------------|----------------|
| Flask | HTTP framework | Expose admin operations | HTTP | JSON | Query endpoint catches and returns exception text. |
| SQLite | Database | Reset and execute SQL | SQL over in-process connection | Rows/commit | Reset has no local exception handling; query catches broad exceptions. |

## Design Patterns & Architecture

| Pattern | Implementation | Location | Purpose |
|---------|----------------|----------|---------|
| Operational endpoint | Admin behavior is exposed as HTTP routes. | `app.py:47-78` | Runtime database operations. |
| Direct database access | App layer bypasses model layer for admin actions. | `app.py:49-69` | Immediate DB control. |

## Technical Debt & Risks

| Risk Level | Component Area | Issue | Impact |
|------------|----------------|-------|--------|
| Critical | Query endpoint | Arbitrary SQL execution. | Complete database read/write exposure. |
| Critical | Reset endpoint | Destructive operation exposed via HTTP. | Full data deletion exposure. |
| High | Authorization boundary | No visible access control. | Admin capabilities are not separated from public app. |
| Medium | Error handling | Database errors returned to clients. | Internal implementation disclosure. |

## Test Coverage Analysis

| Component | Unit Tests | Integration Tests | Coverage | Test Quality |
|-----------|------------|-------------------|----------|--------------|
| Administrative Operations | Not found | Not found | No tests found in scope | No tests for destructive behavior, authorization boundary, or SQL execution behavior were found. |
