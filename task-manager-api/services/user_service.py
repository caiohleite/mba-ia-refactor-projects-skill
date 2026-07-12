from exceptions import ConflictError, ForbiddenError, NotFoundError
from models.user import User
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.validators import validate_user_payload


class UserService:
    def __init__(self, user_repository=UserRepository, task_repository=TaskRepository):
        self.users = user_repository
        self.tasks = task_repository

    def list_users(self):
        return self.users.list_all(with_tasks=True)

    def get_user(self, user_id, actor):
        self._ensure_self_or_role(actor, user_id, {"admin", "manager"})
        user = self.users.get(user_id, with_tasks=True)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        return user

    def create_user(self, payload, actor=None):
        data = validate_user_payload(payload)
        requested_role = data.get("role", "user")
        if requested_role != "user" and (not actor or actor.role != "admin"):
            raise ForbiddenError("Somente administradores podem definir roles privilegiados")
        if self.users.find_by_email(data["email"]):
            raise ConflictError("Email já cadastrado")
        password = data.pop("password")
        user = User(**data)
        user.set_password(password)
        self.users.add(user)
        self._commit()
        return user

    def update_user(self, user_id, payload, actor):
        self._ensure_self_or_role(actor, user_id, {"admin"})
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        data = validate_user_payload(payload, partial=True)
        if {"role", "active"}.intersection(data) and actor.role != "admin":
            raise ForbiddenError("Somente administradores podem alterar role ou atividade")
        if "email" in data:
            existing = self.users.find_by_email(data["email"])
            if existing and existing.id != user_id:
                raise ConflictError("Email já cadastrado")
        password = data.pop("password", None)
        for field, value in data.items():
            setattr(user, field, value)
        if password is not None:
            user.set_password(password)
        self._commit()
        return user

    def delete_user(self, user_id, actor):
        self._ensure_role(actor, {"admin"})
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        self.users.delete_with_tasks(user)
        self._commit()

    def get_user_tasks(self, user_id, actor):
        self._ensure_self_or_role(actor, user_id, {"admin", "manager"})
        if not self.users.get(user_id):
            raise NotFoundError("Usuário não encontrado")
        return self.tasks.list_by_user(user_id)

    @staticmethod
    def _ensure_role(actor, roles):
        if not actor or actor.role not in roles:
            raise ForbiddenError()

    @staticmethod
    def _ensure_self_or_role(actor, user_id, roles):
        if not actor or (actor.id != user_id and actor.role not in roles):
            raise ForbiddenError()

    def _commit(self):
        try:
            self.users.commit()
        except Exception:
            self.users.rollback()
            raise

