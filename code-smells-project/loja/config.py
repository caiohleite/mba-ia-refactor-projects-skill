import os
import secrets


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_tuple(value):
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG", "false"))
    DATABASE = os.environ.get("DATABASE_PATH", "loja.db")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
    AUTO_INIT_DATABASE = _as_bool(os.environ.get("AUTO_INIT_DATABASE", "false"))
    SEED_DATA = _as_bool(os.environ.get("SEED_DATA", "false"))
    SEED_ADMIN_NAME = os.environ.get("SEED_ADMIN_NAME", "Administrator")
    SEED_ADMIN_EMAIL = os.environ.get("SEED_ADMIN_EMAIL")
    SEED_ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD")
    CORS_ORIGINS = _as_tuple(os.environ.get("CORS_ORIGINS", ""))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool(os.environ.get("SESSION_COOKIE_SECURE", "false"))
    ENVIRONMENT = os.environ.get("APP_ENV", "development")
    JSON_SORT_KEYS = False
