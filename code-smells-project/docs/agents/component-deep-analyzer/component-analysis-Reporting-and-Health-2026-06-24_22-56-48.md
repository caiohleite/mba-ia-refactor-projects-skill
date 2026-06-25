# Component Deep Analysis Report

**Component**: Reporting and Health

**Generated on**: 2026-06-24 22:56:48

## Executive Summary

Reporting and Health spans `controllers.py:257-292` and `models.py:235-273`. It exposes a sales report endpoint and a health check endpoint that verifies database connectivity and returns table counts.

The reporting side is read-only and computes aggregate sales metrics. The health side exposes operational details, including database path, debug flag, and secret key, in `controllers.py:285-289`.

## Data Flow Analysis

`relatorio_vendas()` in the controller delegates to `models.relatorio_vendas()`, which performs aggregate SQL queries and returns a metrics dictionary. `health_check()` uses `get_db()` directly, runs test/count queries, and returns status plus internal metadata.

## Overview of the business rules

| Rule Type | Rule Description | Location |
|-----------|------------------|----------|
| Sales count | Count total orders. | `models.py:239-240` |
| Gross revenue | Sum order totals and normalize null to zero. | `models.py:242-245` |
| Status counts | Count pending, approved, and canceled orders. | `models.py:247-254` |
| Discount tiers | Apply 10%, 5%, or 2% discount based on revenue thresholds. | `models.py:256-263` |
| Ticket average | Average ticket equals revenue divided by order count when count is positive. | `models.py:272` |
| Health counts | Return counts for products, users, and orders. | `controllers.py:268-274` |

## Detailed breakdown of the business rules

### Business Rule: Sales Metrics

**Overview**:
Sales reporting returns aggregate order and revenue metrics.

**Detailed description**:
The model counts all orders and sums the `total` column. A missing sum is converted to zero, covering the empty-order case.

It separately counts orders with status `pendente`, `aprovado`, and `cancelado`. Statuses accepted elsewhere, such as `enviado` and `entregue`, are not represented as separate counters in this report.

The report computes gross revenue, applicable discount, net revenue, status counts, and average ticket. Financial values are rounded to two decimals.

**Rule workflow**:
Run aggregate queries -> normalize revenue -> apply tiered discount -> compute average -> return report dictionary.

### Business Rule: Health Probe

**Overview**:
The health endpoint validates DB connectivity and returns table counts.

**Detailed description**:
The controller obtains the shared database connection and executes `SELECT 1`. It then counts rows in `produtos`, `usuarios`, and `pedidos`.

The success response includes status, database state, counts, version, environment label, database path, debug flag, and the secret key value.

If an exception occurs, the endpoint returns status `erro` and includes exception details in the response body.

**Rule workflow**:
GET `/health` -> get DB -> run probe/count queries -> return metadata and counts -> return error details on exception.

## Component Structure

| File | Responsibility |
|------|----------------|
| `controllers.py:257-292` | HTTP wrappers for report and health. |
| `models.py:235-273` | Sales aggregate calculation. |

## Dependency Analysis

- Internal dependencies: `models.relatorio_vendas`, `database.get_db`.
- External dependencies: Flask `jsonify`; SQLite through shared connection.

## Afferent and Efferent Coupling

| Component | Afferent Coupling | Efferent Coupling | Critical |
|-----------|-------------------|-------------------|----------|
| `controllers.relatorio_vendas()` | 1 route | `models.relatorio_vendas` | Medium |
| `models.relatorio_vendas()` | 1 controller | SQLite `pedidos` table | Medium |
| `controllers.health_check()` | 1 route | `get_db`, SQLite tables | Yes |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/relatorios/vendas` | GET | Returns order count, revenue, discount, status counts, and ticket average. |
| `/health` | GET | Returns DB connectivity status, counts, and internal metadata. |

## Integration Points

| Integration | Type | Purpose | Protocol | Data Format | Error Handling |
|-------------|------|---------|----------|-------------|----------------|
| SQLite | Database | Aggregate report and health counts | SQL | Rows/scalars | Broad exception handling in controller endpoints. |
| Flask | HTTP API | Expose report and health responses | HTTP | JSON | Exceptions serialized as response details. |

## Design Patterns & Architecture

| Pattern | Implementation | Location | Purpose |
|---------|----------------|----------|---------|
| Reporting query | Aggregate SQL queries in model function. | `models.py:235-273` | Produce read-only metrics. |
| Health endpoint | Direct DB probe and metadata response. | `controllers.py:264-292` | Runtime status check. |

## Technical Debt & Risks

| Risk Level | Component Area | Issue | Impact |
|------------|----------------|-------|--------|
| High | Health response | Secret key is returned in response. | Secret disclosure. |
| Medium | Health response | Debug flag and DB path are returned. | Operational detail exposure. |
| Medium | Reporting | Report omits `enviado` and `entregue` status counts. | Incomplete operational status view. |
| Low | Reporting | Discount rule is hardcoded in model logic. | Rule changes require source change. |

## Test Coverage Analysis

| Component | Unit Tests | Integration Tests | Coverage | Test Quality |
|-----------|------------|-------------------|----------|--------------|
| Reporting and Health | Not found | Not found | No tests found in scope | No tests for discount thresholds, empty revenue, health response shape, or error behavior were found. |
