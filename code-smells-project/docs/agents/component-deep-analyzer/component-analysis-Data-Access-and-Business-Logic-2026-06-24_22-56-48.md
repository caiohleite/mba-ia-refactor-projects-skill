# Component Deep Analysis Report

**Component**: Data Access and Business Logic

**Generated on**: 2026-06-24 22:56:48

## Executive Summary

This component is implemented in `models.py`. It combines raw SQL data access with business workflows for products, users, login, order creation, stock updates, status updates, product search, and sales reporting.

The component has high architectural criticality because all controller workflows depend on it and because it directly constructs SQL statements. SQL string concatenation appears in product lookup and mutation, login, user creation, order creation, status update, and search flows.

## Data Flow Analysis

Controllers pass primitive values and dictionaries into `models.py`. Each function obtains the shared SQLite connection through `get_db()`, executes SQL, converts rows to dictionaries, and returns plain Python objects to controllers. Order creation performs a multi-step write workflow: validate each product, compute total, insert order, insert order items, decrement stock, commit.

## Overview of the business rules

| Rule Type | Rule Description | Location |
|-----------|------------------|----------|
| Product read model | Product rows are returned with id, name, description, price, stock, category, active flag, and creation timestamp. | `models.py:4-22`, `models.py:24-41`, `models.py:301-314` |
| Login matching | User login requires matching email and password in one SQL query. | `models.py:105-120` |
| Order product existence | Each item's product must exist before an order is created. | `models.py:139-143` |
| Inventory sufficiency | Product stock must be greater than or equal to requested quantity. | `models.py:144-145` |
| Order total calculation | Total equals sum of product price times item quantity. | `models.py:137-146` |
| Stock decrement | Each ordered product stock is decremented by item quantity. | `models.py:163-166` |
| Sales discount tiers | Report discount is 10% over 10000, 5% over 5000, 2% over 1000. | `models.py:256-263` |

## Detailed breakdown of the business rules

### Business Rule: Order Creation and Stock Decrement

**Overview**:
Orders are created only when every referenced product exists and has sufficient stock.

**Detailed description**:
The function iterates over each submitted item and selects the product by `produto_id`. If a product is missing, the function returns an error dictionary and does not create the order. If stock is insufficient, it also returns an error dictionary.

After validation, the function inserts a `pedidos` row with status `pendente` and the calculated total. It then inserts one `itens_pedido` row per item using the current product price.

For each item, product stock is decremented in the `produtos` table. The commit occurs after all inserts and updates. There is no explicit transaction rollback handling in the inspected function.

**Rule workflow**:
Validate products and stock -> calculate total -> insert order -> insert items -> decrement stock -> commit -> return order id and total.

### Business Rule: Sales Discount Calculation

**Overview**:
The sales report computes a discount based on gross revenue thresholds.

**Detailed description**:
The function aggregates total order count and total revenue from the `pedidos` table. If revenue is missing, it is normalized to zero.

It counts orders by selected statuses: `pendente`, `aprovado`, and `cancelado`. Other valid statuses, such as `enviado` and `entregue`, are not included as separate counters in the returned report.

Discount tiers are mutually exclusive and based only on gross revenue: 10% above 10000, 5% above 5000, and 2% above 1000. Net revenue is calculated as gross revenue minus the applicable discount.

**Rule workflow**:
Read aggregate counts and sum -> normalize null revenue -> apply tiered discount -> return rounded financial metrics.

## Component Structure

| File | Responsibility |
|------|----------------|
| `models.py` | Raw SQL queries, row mapping, product/user/order/report business operations. |

## Dependency Analysis

- Internal dependency: `database.get_db`.
- External dependency: Python standard library `sqlite3`, imported at `models.py:2`.

## Afferent and Efferent Coupling

| Component | Afferent Coupling | Efferent Coupling | Critical |
|-----------|-------------------|-------------------|----------|
| `models.py` | 1 (`controllers.py`) | 2 (`database`, `sqlite3`) | Yes |
| Product functions | Controller product handlers | SQLite tables `produtos` | Yes |
| User/login functions | Controller user/login handlers | SQLite table `usuarios` | Yes |
| Order functions | Controller order handlers | SQLite tables `pedidos`, `itens_pedido`, `produtos` | Yes |
| Reporting functions | Controller report handler | SQLite table `pedidos` | Medium |

## Integration Points

| Integration | Type | Purpose | Protocol | Data Format | Error Handling |
|-------------|------|---------|----------|-------------|----------------|
| SQLite | Embedded database | Persistent data storage and queries | In-process SQL | Rows/dicts | Errors propagate to controllers. |
| `database.get_db` | Internal infrastructure helper | Shared connection access | Function call | `sqlite3.Connection` | No local connection error handling. |

## Design Patterns & Architecture

| Pattern | Implementation | Location | Purpose |
|---------|----------------|----------|---------|
| Table Data Gateway style | Functions operate directly on database tables. | `models.py` | Encapsulates SQL per operation. |
| Transaction script | Order creation combines validation, inserts, stock update, and commit. | `models.py:133-169` | Implements an end-to-end use case in one function. |

## Technical Debt & Risks

| Risk Level | Component Area | Issue | Impact |
|------------|----------------|-------|--------|
| High | SQL construction | SQL strings concatenate input values. | SQL injection and malformed query exposure. |
| High | Authentication | Plaintext password matching. | Credential confidentiality risk. |
| Medium | Transactions | Order creation has no explicit rollback path. | Partial write risk on mid-flow failure. |
| Medium | Cohesion | Data access and business rules live in one module. | Broad blast radius for changes. |
| Medium | Read performance | Order listing performs nested queries per order/item. | N+1 query behavior as data grows. |

## Test Coverage Analysis

| Component | Unit Tests | Integration Tests | Coverage | Test Quality |
|-----------|------------|-------------------|----------|--------------|
| Data Access and Business Logic | Not found | Not found | No tests found in scope | No tests for order transaction behavior, SQL query behavior, or reporting calculations were found. |
