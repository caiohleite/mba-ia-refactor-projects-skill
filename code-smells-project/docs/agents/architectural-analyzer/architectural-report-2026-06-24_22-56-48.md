# Architectural Analysis Report

**Generated on**: 2026-06-24 22:56:48

## Executive Summary

`code-smells-project` is a small Python/Flask e-commerce API implemented as a monolithic application. The system has one Flask bootstrap module (`app.py`), one HTTP controller module (`controllers.py`), one combined persistence and business-logic module (`models.py`), and one SQLite initialization module (`database.py`).

The dominant architecture is a simple layered monolith with route registration, controller handlers, model/persistence functions, and SQLite storage. The layering is shallow: controllers call model functions directly, while `models.py` combines data access and business rules for product catalog, users, authentication, orders, and reporting.

The most significant architectural risks are concentrated around security boundaries and persistence coupling: global debug configuration and hardcoded secrets in `app.py:7-8`, permissive CORS in `app.py:9`, unauthenticated administrative endpoints in `app.py:47-78`, direct SQL string concatenation in `models.py:28-299`, and a single global SQLite connection in `database.py:4-10`.

## System Overview

Project structure within scope:

```text
.
|-- README.md
|-- requirements.txt
|-- app.py
|-- controllers.py
|-- models.py
`-- database.py
```

Identified architectural pattern:

- Monolithic Flask API: one process exposes all routes and performs all business operations.
- Layered structure by file: `app.py` registers routes, `controllers.py` handles HTTP request/response flow, `models.py` handles persistence and domain logic, and `database.py` initializes SQLite schema and seed data.
- Active Record is not present. There are no model classes or ORM mappings; persistence is performed through raw SQL functions.

## Critical Components Analysis

Afferent coupling counts incoming module-level dependencies from other project modules. Efferent coupling counts outgoing module-level dependencies to other project modules or external runtime libraries visible in source imports and route calls.

| Component | Type | Location | Afferent Coupling | Efferent Coupling | Architectural Role |
|-----------|------|----------|-------------------|-------------------|--------------------|
| Application Bootstrap and Routing | Flask entrypoint | `app.py` | 0 | 4 | Creates the Flask app, configures CORS/debug/secret, registers public and admin routes, and starts the runtime server. |
| HTTP Controllers | Presentation/API layer | `controllers.py` | 1 | 3 | Converts Flask requests into model calls and JSON responses for products, users, orders, reports, and health checks. |
| Data Access and Business Logic | Persistence/domain layer | `models.py` | 1 | 2 | Executes SQL and contains business rules for product validation support, authentication, order creation, stock decrement, status updates, and sales report calculations. |
| Database Initialization | Infrastructure/persistence | `database.py` | 3 | 2 | Owns global SQLite connection, creates tables, and seeds default products and users. |
| Administrative Operations | Operational endpoint group | `app.py:47-78` | 0 | 2 | Provides database reset and arbitrary SQL execution via HTTP endpoints. |
| Reporting and Health | Read-only API group | `controllers.py:257-292`, `models.py:235-273` | 1 | 2 | Exposes sales aggregate reporting and database health/count checks. |

## Dependency Mapping

Runtime dependency flow:

```text
HTTP client
  -> app.py Flask routes
  -> controllers.py handlers
  -> models.py SQL/business functions
  -> database.py get_db()
  -> loja.db SQLite file
```

Module dependencies:

- `app.py` imports Flask, `CORS`, `controllers`, and `get_db`.
- `controllers.py` imports Flask request/response helpers, `models`, and `get_db`.
- `models.py` imports `get_db` and `sqlite3`; `sqlite3` is not used directly beyond import.
- `database.py` imports `sqlite3` and `os`; `os` is imported but not used in the inspected code.

Control flow is synchronous request/response. There are no queues, background workers, external services, or asynchronous processing constructs in the project files.

## Integration Points

| Integration | Type | Location | Purpose | Risk Level |
|-------------|------|----------|---------|------------|
| Flask HTTP API | Web framework | `app.py:6-88`, `controllers.py:5-292` | Exposes product, user, login, order, report, health, and admin endpoints. | High |
| Browser/API clients via CORS | Cross-origin HTTP | `app.py:9` | Enables cross-origin requests for the Flask app. | Medium |
| SQLite database file `loja.db` | Embedded database | `database.py:4-10`, `README.md:12` | Stores products, users, orders, and order items. | High |
| Admin SQL endpoint | Operational database interface | `app.py:59-78` | Executes arbitrary SQL received in request body. | High |
| Console notification simulation | stdout side effect | `controllers.py:208-210`, `controllers.py:247-250` | Simulates email, SMS, push, and status notifications through `print`. | Low |

## Architectural Risks & Single Points of Failure

| Risk Level | Component | Issue | Impact | Details |
|------------|-----------|-------|--------|---------|
| High | Administrative Operations | Arbitrary SQL execution endpoint | Full database confidentiality and integrity boundary is exposed through HTTP. | `app.py:59-78` executes the submitted `sql` field directly and commits non-SELECT statements. |
| High | Data Access and Business Logic | SQL string concatenation | User-controlled values can reach SQL text in multiple flows. | Examples include `models.py:47-49`, `models.py:109-110`, and `models.py:289-299`. |
| High | Application Bootstrap and Routing | Debug and secret are hardcoded | Runtime configuration and secret material are embedded in source. | `app.py:7-8` and `app.py:88`. |
| High | Database Initialization | Single global SQLite connection | The database connection is process-global and opened with `check_same_thread=False`. | `database.py:4-10`. |
| Medium | HTTP Controllers | Business validation scattered in handlers | Validation rules for products, users, orders, and status transitions are embedded in route handlers. | `controllers.py:24-255`. |
| Medium | Reporting and Health | Health endpoint exposes internals | Database path, debug flag, and secret value are returned in health response. | `controllers.py:276-290`. |

## Technology Stack Assessment

- Language: Python.
- Web framework: Flask declared in `requirements.txt:1`.
- CORS extension: flask-cors declared in `requirements.txt:2`.
- Database: SQLite through Python standard library `sqlite3`.
- Deployment/runtime: README documents local execution with `python app.py`; no production server, container, process manager, infrastructure, or environment configuration files were found.

The stack is small and locally runnable. There is no evidence of dependency injection, ORM usage, migration tooling, authentication middleware, authorization middleware, request schema validation library, or test framework configuration in the inspected project.

## Security Architecture and Risks

There is no explicit authentication or authorization boundary around the product, user, order, report, admin, or health routes. The `/login` route validates credentials by querying the users table with email and password values, but there is no token/session issuance or route protection visible in source.

Credential and secret handling risks are present: stored user passwords are returned by user listing and lookup functions in `models.py:79-85` and `models.py:95-101`; the login query compares plaintext password values in `models.py:109-110`; the Flask secret is hardcoded in `app.py:7`; and the health response exposes `secret_key` in `controllers.py:285-289`.

Database security risks are central to the architecture. Most persistence functions concatenate values into SQL strings, and the admin query endpoint directly executes client-submitted SQL. These findings are based on source inspection rather than dynamic exploit testing.

## Infrastructure Analysis

No Dockerfile, Compose file, CI configuration, deployment manifest, environment file, migration folder, or infrastructure-as-code file was found inside the selected scope. The only runtime instructions are in `README.md:7-12`, which describe installing `requirements.txt` and running `python app.py`.
