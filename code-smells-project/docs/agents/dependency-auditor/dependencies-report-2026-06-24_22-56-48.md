# Dependency Audit Report

**Generated on**: 2026-06-24 22:56:48

## Summary

The project uses a Python dependency manifest at `requirements.txt` with two direct runtime dependencies: `flask==3.1.1` and `flask-cors==5.0.1`. No lockfile was found, so reproducible transitive dependency resolution is not guaranteed from repository contents alone.

External version verification was performed against PyPI. PyPI lists Flask `3.1.3` as the latest release, published on 2026-02-19, with license expression `BSD-3-Clause` and Python requirement `>=3.9`. PyPI lists flask-cors `6.0.5` as the latest release, published on 2026-06-08, with license expression `MIT` and Python requirement `>=3.9,<4.0`.

The highest dependency-related operational risks are not CVEs in the declared direct dependencies, but the way the framework dependencies are used: global CORS is enabled in `app.py:9`, debug mode and a hardcoded secret are configured in `app.py:7-8`, and administrative endpoints expose database reset and arbitrary SQL execution in `app.py:47-78`.

## Critical Issues

No verified CVE was identified for the exact declared direct dependencies during this audit. CVE database checks could not be completed through a local vulnerability scanner because the workflow is report-only and no dependency tooling or lockfile output was available in the repository.

Critical dependency-adjacent issues observed in source usage:

- `Flask` is used with `DEBUG=True` and `app.run(..., debug=True)` in `app.py:8` and `app.py:88`.
- `Flask` app secret is hardcoded in `app.py:7`.
- `flask-cors` is initialized globally with `CORS(app)` in `app.py:9`, applying permissive cross-origin behavior across routes.
- Admin routes reachable through the Flask app include destructive reset and arbitrary SQL execution in `app.py:47-78`.

## Dependencies

| Dependency | Current Version | Latest Version | Status |
|------------|-----------------|----------------|--------|
| Flask | 3.1.1 | 3.1.3 | Behind latest stable; externally verified on PyPI |
| flask-cors | 5.0.1 | 6.0.5 | Behind latest stable; externally verified on PyPI |

## Risk Analysis

| Severity | Dependency | Issue | Details |
|----------|------------|-------|---------|
| High | Flask | Debug and secret configuration exposed through application code | `app.py:7-8` configures a hardcoded secret and debug mode; `app.py:88` starts the server with debug enabled. |
| High | Flask | Arbitrary SQL endpoint exposed through the web framework | `app.py:59-78` accepts request JSON and executes the `sql` field directly against SQLite. |
| Medium | flask-cors | Global CORS configuration | `app.py:9` applies `CORS(app)` globally. The project does not define origin restrictions in repository configuration. |
| Medium | Flask | No lockfile for transitive dependency reproducibility | `requirements.txt` pins direct dependencies only; no lockfile was found for resolved transitive versions. |
| Low | Flask | Declared version is not latest stable | `requirements.txt:1` declares `3.1.1`; PyPI lists `3.1.3` as latest. |
| Low | flask-cors | Declared version is not latest stable | `requirements.txt:2` declares `5.0.1`; PyPI lists `6.0.5` as latest. |

## Critical File Analysis

| File | Dependency Exposure | Rationale |
|------|---------------------|-----------|
| `app.py` | Flask, flask-cors | Central application bootstrap, route registration, CORS initialization, debug configuration, hardcoded secret, admin endpoints, and arbitrary SQL execution. |
| `controllers.py` | Flask | All HTTP handlers depend on `request` and `jsonify`; exceptions are often returned directly to clients. |
| `database.py` | sqlite3 stdlib | Global SQLite connection and schema initialization are used by all request flows. |
| `models.py` | sqlite3 stdlib through `database.get_db` | Contains direct SQL construction, business logic, and persistence operations used by controllers. |
| `requirements.txt` | Python package manifest | Pins only direct dependencies and has no companion lockfile. |
| `README.md` | Runtime setup documentation | Documents `pip install -r requirements.txt` and `python app.py`, confirming direct local runtime execution. |

Fewer than ten critical dependency-consuming files exist in the project scope after applying ignore folders.

## Integration Notes

- `Flask` provides the web application object, route registration, request access, JSON responses, and server execution. Usage appears in `app.py:1`, `app.py:6-30`, `app.py:32-88`, and `controllers.py:1`.
- `flask-cors` is used only in `app.py:2` and initialized globally in `app.py:9`.
- `sqlite3` is a Python standard library dependency, not a declared package dependency. It is used in `database.py:1` and imported in `models.py:2`; all database access goes through the `get_db()` helper from `database.py`.

## Verification Sources

- PyPI project page for Flask, accessed during this audit: `https://pypi.org/project/Flask/`
- PyPI project page for flask-cors, accessed during this audit: `https://pypi.org/project/Flask-Cors/`

## Unverified Dependencies

No direct dependency version was left unverified for latest-version metadata. CVE status remains partially unverified because no lockfile or local vulnerability scanner output was available in the repository and no CVE identifiers were confirmed for the declared versions during this audit.
