from flask import current_app, g, jsonify, request

from exceptions import ValidationError
from schemas.serializers import user_task_to_dict, user_to_dict
from schemas.validators import require_payload
from services.auth_service import AuthService
from services.user_service import UserService


class UserController:
    service = UserService()

    @classmethod
    def list_users(cls):
        users = cls.service.list_users()
        return jsonify([user_to_dict(user, include_task_count=True) for user in users]), 200

    @classmethod
    def get_user(cls, user_id):
        user = cls.service.get_user(user_id, g.current_user)
        return jsonify(user_to_dict(user, include_tasks=True)), 200

    @classmethod
    def create_user(cls):
        user = cls.service.create_user(
            request.get_json(silent=True), actor=getattr(g, "current_user", None)
        )
        return jsonify(user_to_dict(user)), 201

    @classmethod
    def update_user(cls, user_id):
        user = cls.service.update_user(
            user_id, request.get_json(silent=True), g.current_user
        )
        return jsonify(user_to_dict(user)), 200

    @classmethod
    def delete_user(cls, user_id):
        cls.service.delete_user(user_id, g.current_user)
        return jsonify({"message": "Usuário deletado com sucesso"}), 200

    @classmethod
    def get_user_tasks(cls, user_id):
        tasks = cls.service.get_user_tasks(user_id, g.current_user)
        return jsonify([user_task_to_dict(task) for task in tasks]), 200

    @classmethod
    def login(cls):
        payload = require_payload(request.get_json(silent=True))
        email = payload.get("email")
        password = payload.get("password")
        if not email or not password:
            raise ValidationError("Email e senha são obrigatórios")
        user, token = cls._auth_service().authenticate(email, password)
        return jsonify(
            {
                "message": "Login realizado com sucesso",
                "user": user_to_dict(user),
                "token": token,
            }
        ), 200

    @staticmethod
    def _auth_service():
        return AuthService(
            current_app.config["SECRET_KEY"],
            current_app.config.get("AUTH_TOKEN_MAX_AGE", 3600),
        )

