class APIError(Exception):
    status_code = 500
    default_message = "Erro interno"

    def __init__(self, message=None, status_code=None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(APIError):
    status_code = 400
    default_message = "Dados inválidos"


class UnauthorizedError(APIError):
    status_code = 401
    default_message = "Autenticação necessária"


class ForbiddenError(APIError):
    status_code = 403
    default_message = "Acesso negado"


class NotFoundError(APIError):
    status_code = 404
    default_message = "Recurso não encontrado"


class ConflictError(APIError):
    status_code = 409
    default_message = "Conflito"

