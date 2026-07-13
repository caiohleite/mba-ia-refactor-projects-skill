from exceptions import NotFoundError
from models.task import Task
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.validators import parse_optional_int, validate_task_payload
from utils.time import utc_now


class TaskService:
    def __init__(
        self,
        task_repository=TaskRepository,
        user_repository=UserRepository,
        category_repository=CategoryRepository,
    ):
        self.tasks = task_repository
        self.users = user_repository
        self.categories = category_repository

    def list_tasks(self):
        return self.tasks.list_all(with_relations=True)

    def get_task(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        return task

    def create_task(self, payload):
        data = validate_task_payload(payload)
        self._validate_relations(data)
        task = Task(**data)
        self.tasks.add(task)
        self._commit()
        return task

    def update_task(self, task_id, payload):
        task = self.get_task(task_id)
        data = validate_task_payload(payload, partial=True)
        self._validate_relations(data)
        for field, value in data.items():
            setattr(task, field, value)
        task.updated_at = utc_now()
        self._commit()
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        self.tasks.delete(task)
        self._commit()

    def search_tasks(self, query=None, status=None, priority=None, user_id=None):
        return self.tasks.search(
            query=query,
            status=status,
            priority=parse_optional_int(priority, "Prioridade"),
            user_id=parse_optional_int(user_id, "Usuário"),
        )

    def task_stats(self):
        total = self.tasks.total_count()
        counts = self.tasks.status_counts()
        done = counts.get("done", 0)
        return {
            "total": total,
            "pending": counts.get("pending", 0),
            "in_progress": counts.get("in_progress", 0),
            "done": done,
            "cancelled": counts.get("cancelled", 0),
            "overdue": self.tasks.overdue_count(utc_now()),
            "completion_rate": round((done / total) * 100, 2) if total else 0,
        }

    def _validate_relations(self, data):
        if "user_id" in data and data["user_id"] is not None:
            if not self.users.get(data["user_id"]):
                raise NotFoundError("Usuário não encontrado")
        if "category_id" in data and data["category_id"] is not None:
            if not self.categories.get(data["category_id"]):
                raise NotFoundError("Categoria não encontrada")

    def _commit(self):
        try:
            self.tasks.commit()
        except Exception:
            self.tasks.rollback()
            raise

