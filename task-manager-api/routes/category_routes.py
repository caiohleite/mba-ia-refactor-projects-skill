from flask import Blueprint

from controllers.category_controller import CategoryController
from middlewares.auth import roles_required


category_bp = Blueprint("categories", __name__)


@category_bp.get("/categories")
def get_categories():
    return CategoryController.list_categories()


@category_bp.post("/categories")
@roles_required("admin")
def create_category():
    return CategoryController.create_category()


@category_bp.put("/categories/<int:category_id>")
@roles_required("admin")
def update_category(category_id):
    return CategoryController.update_category(category_id)


@category_bp.delete("/categories/<int:category_id>")
@roles_required("admin")
def delete_category(category_id):
    return CategoryController.delete_category(category_id)
