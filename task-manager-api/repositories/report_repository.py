from sqlalchemy import case

from database import db
from models.category import Category
from models.task import Task
from models.user import User


class ReportRepository:
    @staticmethod
    def entity_counts():
        return {
            "total_tasks": db.session.scalar(db.select(db.func.count(Task.id))) or 0,
            "total_users": db.session.scalar(db.select(db.func.count(User.id))) or 0,
            "total_categories": db.session.scalar(db.select(db.func.count(Category.id))) or 0,
        }

    @staticmethod
    def grouped_task_counts(column):
        statement = db.select(column, db.func.count(Task.id)).group_by(column)
        return dict(db.session.execute(statement).all())

    @staticmethod
    def overdue_tasks(now):
        statement = db.select(Task).where(
            Task.due_date.is_not(None),
            Task.due_date < now,
            Task.status.not_in(("done", "cancelled")),
        )
        return db.session.execute(statement).scalars().all()

    @staticmethod
    def recent_counts(since):
        created = db.session.scalar(
            db.select(db.func.count(Task.id)).where(Task.created_at >= since)
        ) or 0
        completed = db.session.scalar(
            db.select(db.func.count(Task.id)).where(
                Task.status == "done", Task.updated_at >= since
            )
        ) or 0
        return created, completed

    @staticmethod
    def user_productivity():
        completed = db.func.coalesce(
            db.func.sum(case((Task.status == "done", 1), else_=0)), 0
        )
        statement = (
            db.select(User.id, User.name, db.func.count(Task.id), completed)
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id, User.name)
        )
        return db.session.execute(statement).all()

