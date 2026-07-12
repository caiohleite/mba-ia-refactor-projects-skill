from datetime import timedelta

from exceptions import ForbiddenError, NotFoundError
from models.task import Task
from repositories.report_repository import ReportRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from utils.time import utc_now


class ReportService:
    def __init__(
        self,
        report_repository=ReportRepository,
        task_repository=TaskRepository,
        user_repository=UserRepository,
    ):
        self.reports = report_repository
        self.tasks = task_repository
        self.users = user_repository

    def summary(self, actor):
        self._ensure_role(actor, {"admin", "manager"})
        now = utc_now()
        counts = self.reports.entity_counts()
        by_status = self.reports.grouped_task_counts(Task.status)
        by_priority = self.reports.grouped_task_counts(Task.priority)
        overdue_tasks = self.reports.overdue_tasks(now)
        recent_created, recent_done = self.reports.recent_counts(now - timedelta(days=7))
        productivity = []
        for user_id, user_name, total, completed in self.reports.user_productivity():
            productivity.append(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": round((completed / total) * 100, 2) if total else 0,
                }
            )
        return {
            "generated_at": str(now),
            "overview": counts,
            "tasks_by_status": {
                "pending": by_status.get("pending", 0),
                "in_progress": by_status.get("in_progress", 0),
                "done": by_status.get("done", 0),
                "cancelled": by_status.get("cancelled", 0),
            },
            "tasks_by_priority": {
                "critical": by_priority.get(1, 0),
                "high": by_priority.get(2, 0),
                "medium": by_priority.get(3, 0),
                "low": by_priority.get(4, 0),
                "minimal": by_priority.get(5, 0),
            },
            "overdue": {
                "count": len(overdue_tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "due_date": str(task.due_date),
                        "days_overdue": (now - task.due_date).days,
                    }
                    for task in overdue_tasks
                ],
            },
            "recent_activity": {
                "tasks_created_last_7_days": recent_created,
                "tasks_completed_last_7_days": recent_done,
            },
            "user_productivity": productivity,
        }

    def user_report(self, user_id, actor):
        if not actor or (actor.id != user_id and actor.role not in {"admin", "manager"}):
            raise ForbiddenError()
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        tasks = self.tasks.list_by_user(user_id)
        counts = {"done": 0, "pending": 0, "in_progress": 0, "cancelled": 0}
        overdue = 0
        high_priority = 0
        for task in tasks:
            if task.status in counts:
                counts[task.status] += 1
            if task.priority <= 2:
                high_priority += 1
            if task.is_overdue():
                overdue += 1
        total = len(tasks)
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": {
                "total_tasks": total,
                **counts,
                "overdue": overdue,
                "high_priority": high_priority,
                "completion_rate": round((counts["done"] / total) * 100, 2) if total else 0,
            },
        }

    @staticmethod
    def _ensure_role(actor, roles):
        if not actor or actor.role not in roles:
            raise ForbiddenError()
