from flask import current_app, jsonify
from werkzeug.exceptions import HTTPException

from exceptions import APIError


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        current_app.logger.exception("Erro não tratado", exc_info=error)
        return jsonify({"error": "Erro interno"}), 500

