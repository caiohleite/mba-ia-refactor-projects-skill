from database import db
from models.category import Category
from models.task import Task
from repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    @staticmethod
    def list_all():
        return db.session.execute(db.select(Category)).scalars().all()

    @staticmethod
    def list_with_task_counts():
        statement = (
            db.select(Category, db.func.count(Task.id))
            .outerjoin(Task, Task.category_id == Category.id)
            .group_by(Category.id)
        )
        return db.session.execute(statement).all()

    @staticmethod
    def get(category_id):
        return db.session.get(Category, category_id)

