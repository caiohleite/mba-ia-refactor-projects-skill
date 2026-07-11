from functools import wraps

from flask import g, session

from loja.errors import AuthenticationError, AuthorizationError


def login_user(user):
    session.clear()
    session["principal"] = {"id": int(user["id"]), "tipo": user["tipo"]}


def get_current_user():
    principal = session.get("principal")
    if not isinstance(principal, dict):
        raise AuthenticationError("Autenticação necessária")
    if not isinstance(principal.get("id"), int) or principal.get("tipo") not in {
        "admin",
        "cliente",
    }:
        session.clear()
        raise AuthenticationError("Sessão inválida")
    return principal


def require_auth(*allowed_roles, owner_arg=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            principal = get_current_user()
            if allowed_roles and principal["tipo"] not in allowed_roles:
                raise AuthorizationError("Permissão insuficiente")
            if owner_arg and principal["tipo"] != "admin":
                owner_id = kwargs.get(owner_arg)
                if owner_id != principal["id"]:
                    raise AuthorizationError("Acesso permitido apenas ao próprio recurso")
            g.current_user = principal
            return view(*args, **kwargs)

        return wrapped

    return decorator
