import os
import secrets


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG", "false"))
    DATABASE = os.environ.get("DATABASE_PATH", "loja.db")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
    ENVIRONMENT = os.environ.get("APP_ENV", "development")
    JSON_SORT_KEYS = False
