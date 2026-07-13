from flask import jsonify, request

from schemas.serializers import task_to_dict
from services.task_service import TaskService


class TaskController:
    service = TaskService()

    @classmethod
    def list_tasks(cls):
        tasks = cls.service.list_tasks()
        return jsonify(
            [task_to_dict(task, include_overdue=True, include_relations=True) for task in tasks]
        ), 200

    @classmethod
    def get_task(cls, task_id):
        task = cls.service.get_task(task_id)
        return jsonify(task_to_dict(task, include_overdue=True)), 200

    @classmethod
    def create_task(cls):
        task = cls.service.create_task(request.get_json(silent=True))
        return jsonify(task_to_dict(task)), 201

    @classmethod
    def update_task(cls, task_id):
        task = cls.service.update_task(task_id, request.get_json(silent=True))
        return jsonify(task_to_dict(task)), 200

    @classmethod
    def delete_task(cls, task_id):
        cls.service.delete_task(task_id)
        return jsonify({"message": "Task deletada com sucesso"}), 200

    @classmethod
    def search_tasks(cls):
        tasks = cls.service.search_tasks(
            query=request.args.get("q", ""),
            status=request.args.get("status", ""),
            priority=request.args.get("priority", ""),
            user_id=request.args.get("user_id", ""),
        )
        return jsonify([task_to_dict(task) for task in tasks]), 200

    @classmethod
    def task_stats(cls):
        return jsonify(cls.service.task_stats()), 200

