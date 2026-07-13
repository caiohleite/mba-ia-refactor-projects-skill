from flask import Blueprint

from controllers.task_controller import TaskController
from middlewares.auth import authenticated


task_bp = Blueprint("tasks", __name__)


@task_bp.get("/tasks")
def get_tasks():
    return TaskController.list_tasks()


@task_bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    return TaskController.get_task(task_id)


@task_bp.post("/tasks")
@authenticated
def create_task():
    return TaskController.create_task()


@task_bp.put("/tasks/<int:task_id>")
@authenticated
def update_task(task_id):
    return TaskController.update_task(task_id)


@task_bp.delete("/tasks/<int:task_id>")
@authenticated
def delete_task(task_id):
    return TaskController.delete_task(task_id)


@task_bp.get("/tasks/search")
def search_tasks():
    return TaskController.search_tasks()


@task_bp.get("/tasks/stats")
def task_stats():
    return TaskController.task_stats()
