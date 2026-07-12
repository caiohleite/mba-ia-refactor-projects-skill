from functools import wraps

from flask import current_app, g, request

from exceptions import ForbiddenError, UnauthorizedError
from services.auth_service import AuthService


def _auth_service():
    return AuthService(
        current_app.config["SECRET_KEY"],
        current_app.config.get("AUTH_TOKEN_MAX_AGE", 3600),
    )


def _bearer_token(required=True):
    header = request.headers.get("Authorization", "")
    if not header:
        if required:
            raise UnauthorizedError()
        return None
    scheme, separator, token = header.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise UnauthorizedError("Token inválido")
    return token.strip()


def _load_current_user(required=True):
    current_user = getattr(g, "current_user", None)
    if current_user is not None:
        return current_user
    token = _bearer_token(required=required)
    if token is None:
        g.current_user = None
        return None
    g.current_user = _auth_service().verify_token(token)
    return g.current_user


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        _load_current_user(required=True)
        return view(*args, **kwargs)

    return wrapped


def optional_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        _load_current_user(required=False)
        return view(*args, **kwargs)

    return wrapped


def roles_required(*roles):
    allowed_roles = set(roles)

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = _load_current_user(required=True)
            if user.role not in allowed_roles:
                raise ForbiddenError()
            return view(*args, **kwargs)

        return wrapped

    return decorator
