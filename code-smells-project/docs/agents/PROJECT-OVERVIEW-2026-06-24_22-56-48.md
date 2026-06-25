# code-smells-project - Project Overview

**Generated on**: 2026-06-24 22:56:48

## Summary

`code-smells-project` is a small Python/Flask e-commerce API with product, user, login, order, sales report, health, and administrative database endpoints. The implementation is a single-process monolith composed of `app.py`, `controllers.py`, `models.py`, and `database.py`.

The architecture is a simple layered structure: Flask route registration delegates to controller functions, controller functions call model functions, and model functions use a shared SQLite connection. The layer boundary is incomplete because `app.py` and `controllers.py` also access the database helper directly for admin and health flows.

The dependency set is small: direct runtime dependencies are `Flask==3.1.1` and `flask-cors==5.0.1`. PyPI verification showed both are behind latest stable releases at audit time, and no lockfile was found in the repository.

## Architecture Overview

The system is a procedural Flask API. `app.py` creates the app, configures `SECRET_KEY`, debug mode, CORS, route mappings, and the local server. `controllers.py` handles HTTP input/output and validation. `models.py` combines data access with business logic for products, users, orders, search, and reporting. `database.py` lazily initializes SQLite schema and seed data.

The runtime data flow is synchronous: HTTP client to Flask route, controller, model function, shared SQLite connection, and `loja.db`. No background worker, queue, external API integration, container configuration, migration tooling, or CI/deployment asset was found in scope.

## Dependencies Health

`Flask` is declared at `3.1.1`; PyPI lists `3.1.3` as latest stable. `flask-cors` is declared at `5.0.1`; PyPI lists `6.0.5` as latest stable. The repository does not include a lockfile, so transitive dependency reproducibility cannot be established from source alone.

The highest dependency-related risks are in framework usage: debug mode is enabled, CORS is global, the app secret is hardcoded, and administrative endpoints expose direct database operations.

## Components Analyzed

Application Bootstrap and Routing: Creates the Flask app, registers routes, configures CORS/debug/secret, and starts the server. It also contains root and admin endpoints.

HTTP Controllers: Handles product, user, login, order, report, and health HTTP workflows. It contains validation rules and response formatting logic.

Data Access and Business Logic: Executes raw SQL and implements product/user/order/report operations. It centralizes most persistence and business behavior.

Database Initialization: Opens the shared SQLite connection, creates tables, and seeds default products and users. It is the persistence bootstrap point for the application.

Administrative Operations: Exposes database reset and arbitrary SQL execution through HTTP endpoints in `app.py`. It bypasses controller/model boundaries.

Reporting and Health: Provides sales aggregate reporting and database health/count checks. The health response includes internal metadata.

## Critical Findings

### Security Risks

The application has a hardcoded Flask secret and debug mode enabled in `app.py`. The health endpoint returns `secret_key`, `debug`, and database path values. User passwords are stored and returned as plaintext fields in model responses. SQL is built through string concatenation in multiple model functions, and `/admin/query` executes client-submitted SQL directly.

### Technical Debt

The project mixes HTTP validation, business rules, SQL persistence, and operational behavior across a small set of procedural modules. No tests were found. No lockfile, migration tooling, authentication middleware, authorization checks, schema validation library, or deployment configuration was found in scope.

### Single Points of Failure

`database.py` owns a single global SQLite connection with `check_same_thread=False`. `models.py` is the central dependency for all business and persistence operations. `app.py` is the central route registry and also contains administrative database operations. The SQLite file `loja.db` is the only persistence backend documented by the repository.

## Reports Index

See [MANIFEST.md](./MANIFEST.md) for the complete list of generated reports.
