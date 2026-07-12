from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository):
    @staticmethod
    def list_all(with_relations=False):
        statement = db.select(Task)
        if with_relations:
            statement = statement.options(joinedload(Task.user), joinedload(Task.category))
        return db.session.execute(statement).scalars().all()

    @staticmethod
    def get(task_id):
        return db.session.get(Task, task_id)

    @staticmethod
    def list_by_user(user_id):
        statement = db.select(Task).where(Task.user_id == user_id)
        return db.session.execute(statement).scalars().all()

    @staticmethod
    def search(query=None, status=None, priority=None, user_id=None):
        statement = db.select(Task)
        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                db.or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
            )
        if status:
            statement = statement.where(Task.status == status)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
        if user_id is not None:
            statement = statement.where(Task.user_id == user_id)
        return db.session.execute(statement).scalars().all()

    @staticmethod
    def status_counts():
        statement = db.select(Task.status, db.func.count(Task.id)).group_by(Task.status)
        return dict(db.session.execute(statement).all())

    @staticmethod
    def total_count():
        statement = db.select(db.func.count(Task.id))
        return db.session.scalar(statement) or 0

    @staticmethod
    def overdue_count(now):
        statement = db.select(db.func.count(Task.id)).where(
            Task.due_date.is_not(None),
            Task.due_date < now,
            Task.status.not_in(("done", "cancelled")),
        )
        return db.session.scalar(statement) or 0

