# Component Deep Analysis Report

**Component**: Database Initialization

**Generated on**: 2026-06-24 22:56:48

## Executive Summary

The Database Initialization component is implemented in `database.py`. It owns a global SQLite connection, creates schema tables on first access, and seeds default products and users when the product table is empty.

This component is a single point of failure for all persistence operations. It uses a process-global connection with `check_same_thread=False` at `database.py:10`, stores the database path in source as `loja.db` at `database.py:5`, and defines schema without foreign keys or explicit constraints.

## Data Flow Analysis

Any caller invokes `get_db()`. On first call, the function opens `loja.db`, sets row factory behavior, creates tables if needed, seeds products/users when no products exist, commits, and returns the connection. Subsequent calls return the same global connection object.

## Overview of the business rules

| Rule Type | Rule Description | Location |
|-----------|------------------|----------|
| Lazy initialization | Database is initialized on first `get_db()` call. | `database.py:7-13` |
| Schema creation | Four tables are created if absent: `produtos`, `usuarios`, `pedidos`, `itens_pedido`. | `database.py:14-53` |
| Seed trigger | Seed data is inserted only when product count is zero. | `database.py:56-57` |
| Default products | Ten default product records are inserted. | `database.py:58-73` |
| Default users | Three default users, including admin credentials, are inserted. | `database.py:75-83` |

## Detailed breakdown of the business rules

### Business Rule: Lazy Schema Creation

**Overview**:
The database schema is created when the application first asks for a database connection.

**Detailed description**:
The function checks whether `db_connection` is `None`. If so, it opens an SQLite file at the hardcoded path `loja.db` and configures rows to behave like mapping objects.

It creates tables for products, users, orders, and order items using `CREATE TABLE IF NOT EXISTS`. This means application startup and schema bootstrap are coupled to runtime access rather than to a separate migration step.

The schema defines primary keys and defaults but does not define foreign keys between orders, users, products, and order items in the inspected SQL.

**Rule workflow**:
Call `get_db()` -> open connection if absent -> create tables -> seed if needed -> return connection.

### Business Rule: Seed Data Initialization

**Overview**:
Default catalog and user data are inserted when the product table is empty.

**Detailed description**:
The function counts rows in `produtos`. If the count is zero, it inserts ten products and three users.

The seed user list includes an admin user and two client users with plaintext password values. These seed credentials become part of local database state on first boot.

The seed trigger checks only product count. If users are missing but products exist, the seed user list will not be inserted by this function.

**Rule workflow**:
Count products -> if zero, insert product list and user list -> commit.

## Component Structure

| File | Responsibility |
|------|----------------|
| `database.py` | SQLite connection lifecycle, schema creation, seed data. |

## Dependency Analysis

- External dependencies: Python standard library `sqlite3`, `os`.
- Internal dependents: `app.py`, `controllers.py`, and `models.py`.

## Afferent and Efferent Coupling

| Component | Afferent Coupling | Efferent Coupling | Critical |
|-----------|-------------------|-------------------|----------|
| `database.py` | 3 (`app.py`, `controllers.py`, `models.py`) | 2 (`sqlite3`, `os`) | Yes |
| `get_db()` | 3 modules | SQLite file and schema SQL | Yes |

## Integration Points

| Integration | Type | Purpose | Protocol | Data Format | Error Handling |
|-------------|------|---------|----------|-------------|----------------|
| SQLite file `loja.db` | Embedded database | Store application data | File-backed SQL | SQLite rows | No explicit exception handling in `get_db()`. |

## Design Patterns & Architecture

| Pattern | Implementation | Location | Purpose |
|---------|----------------|----------|---------|
| Lazy singleton | Global connection initialized once. | `database.py:4-10` | Reuse one DB connection. |
| Embedded schema bootstrap | `CREATE TABLE IF NOT EXISTS` inside runtime helper. | `database.py:14-53` | Initialize local DB without migrations. |

## Technical Debt & Risks

| Risk Level | Component Area | Issue | Impact |
|------------|----------------|-------|--------|
| High | Connection lifecycle | Global connection with `check_same_thread=False`. | Cross-request/thread safety risk. |
| High | Seed data | Default plaintext credentials. | Credential exposure risk in generated DB. |
| Medium | Schema integrity | No foreign keys or explicit constraints found. | Orphaned or inconsistent rows can exist. |
| Medium | Configuration | Database path is hardcoded. | Environment-specific deployment is not represented. |

## Test Coverage Analysis

| Component | Unit Tests | Integration Tests | Coverage | Test Quality |
|-----------|------------|-------------------|----------|--------------|
| Database Initialization | Not found | Not found | No tests found in scope | No tests for schema creation, seed trigger, or connection lifecycle were found. |
