from sqlalchemy.orm import selectinload

from database import db
from models.task import Task
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    @staticmethod
    def list_all(with_tasks=False):
        statement = db.select(User)
        if with_tasks:
            statement = statement.options(selectinload(User.tasks))
        return db.session.execute(statement).scalars().all()

    @staticmethod
    def get(user_id, with_tasks=False):
        options = [selectinload(User.tasks)] if with_tasks else None
        return db.session.get(User, user_id, options=options)

    @staticmethod
    def find_by_email(email):
        statement = db.select(User).where(User.email == email)
        return db.session.execute(statement).scalar_one_or_none()

    @staticmethod
    def delete_with_tasks(user):
        db.session.execute(db.delete(Task).where(Task.user_id == user.id))
        db.session.delete(user)

