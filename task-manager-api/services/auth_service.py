from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from exceptions import UnauthorizedError
from repositories.user_repository import UserRepository


class AuthService:
    TOKEN_SALT = "task-manager-auth"

    def __init__(self, secret_key, max_age=3600, user_repository=UserRepository):
        self.serializer = URLSafeTimedSerializer(secret_key, salt=self.TOKEN_SALT)
        self.max_age = max_age
        self.users = user_repository

    def authenticate(self, email, password):
        if not email or not password:
            raise UnauthorizedError("Email e senha são obrigatórios")
        user = self.users.find_by_email(email)
        if not user or not user.check_password(password):
            raise UnauthorizedError("Credenciais inválidas")
        if not user.active:
            raise UnauthorizedError("Usuário inativo", status_code=403)
        if user.has_legacy_password():
            user.set_password(password)
            self._commit()
        return user, self.generate_token(user)

    def generate_token(self, user):
        return self.serializer.dumps({"user_id": user.id})

    def verify_token(self, token):
        if not token:
            raise UnauthorizedError()
        try:
            payload = self.serializer.loads(token, max_age=self.max_age)
        except SignatureExpired as error:
            raise UnauthorizedError("Token expirado") from error
        except BadSignature as error:
            raise UnauthorizedError("Token inválido") from error
        user = self.users.get(payload.get("user_id"))
        if not user or not user.active:
            raise UnauthorizedError("Token inválido")
        return user

    def _commit(self):
        try:
            self.users.commit()
        except Exception:
            self.users.rollback()
            raise

