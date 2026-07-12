from flask import g, jsonify, request

from schemas.serializers import category_to_dict
from services.category_service import CategoryService


class CategoryController:
    service = CategoryService()

    @classmethod
    def list_categories(cls):
        rows = cls.service.list_categories()
        return jsonify(
            [category_to_dict(category, task_count) for category, task_count in rows]
        ), 200

    @classmethod
    def create_category(cls):
        category = cls.service.create_category(
            request.get_json(silent=True), g.current_user
        )
        return jsonify(category_to_dict(category)), 201

    @classmethod
    def update_category(cls, category_id):
        category = cls.service.update_category(
            category_id, request.get_json(silent=True), g.current_user
        )
        return jsonify(category_to_dict(category)), 200

    @classmethod
    def delete_category(cls, category_id):
        cls.service.delete_category(category_id, g.current_user)
        return jsonify({"message": "Categoria deletada"}), 200

