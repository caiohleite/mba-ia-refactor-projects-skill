class ApplicationError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(ApplicationError):
    status_code = 400


class AuthenticationError(ApplicationError):
    status_code = 401


class AuthorizationError(ApplicationError):
    status_code = 403


class NotFoundError(ApplicationError):
    status_code = 404


class ConflictError(ApplicationError):
    status_code = 409


def register_error_handlers(app):
    from flask import jsonify
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(ApplicationError)
    def handle_application_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description, "sucesso": False}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro nao tratado: %s", error)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
