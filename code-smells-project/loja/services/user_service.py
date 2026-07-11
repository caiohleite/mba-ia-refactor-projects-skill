import hmac
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from loja.database import get_db
from loja.errors import AuthenticationError, ConflictError, NotFoundError, ValidationError
from loja.repositories.user_repository import UserRepository
from loja.services.validators import require_object


class UserService:
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def list_users(self):
        return [user.to_public_dict() for user in self.repository.list_all()]

    def get_user(self, user_id):
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado")
        return user.to_public_dict()

    def create_user(self, data):
        data = require_object(data)
        name = data.get("nome", "")
        email = data.get("email", "")
        password = data.get("senha", "")
        if not all(isinstance(value, str) and value.strip() for value in (name, email, password)):
            raise ValidationError("Nome, email e senha são obrigatórios")
        if self.repository.get_by_email(email.strip()) is not None:
            raise ConflictError("Email já cadastrado")

        database = get_db()
        try:
            user_id = self.repository.create(
                name.strip(),
                email.strip(),
                generate_password_hash(password),
            )
            database.commit()
        except sqlite3.IntegrityError as error:
            database.rollback()
            raise ConflictError("Email já cadastrado") from error
        return user_id

    def login(self, data):
        data = require_object(data)
        email = data.get("email", "")
        password = data.get("senha", "")
        if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
            raise ValidationError("Email e senha são obrigatórios")

        user = self.repository.get_by_email(email)
        if user is None or not self._password_matches(user.password_hash, password):
            raise AuthenticationError("Email ou senha inválidos")

        if not self._is_password_hash(user.password_hash):
            self.repository.update_password(user.id, generate_password_hash(password))
            get_db().commit()
        return user.to_login_dict()

    @staticmethod
    def _is_password_hash(stored_value):
        return "$" in stored_value and ":" in stored_value.split("$", 1)[0]

    @classmethod
    def _password_matches(cls, stored_value, candidate):
        if cls._is_password_hash(stored_value):
            return check_password_hash(stored_value, candidate)
        return hmac.compare_digest(stored_value, candidate)
