import os
import secrets


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    AUTH_TOKEN_MAX_AGE = _as_int(os.getenv("AUTH_TOKEN_MAX_AGE"), 3600)
    DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), default=False)
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = _as_int(os.getenv("PORT"), 5000)

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = _as_int(os.getenv("SMTP_PORT"), 587)
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
