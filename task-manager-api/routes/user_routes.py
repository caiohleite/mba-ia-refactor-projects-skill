from flask import Blueprint

from controllers.user_controller import UserController
from middlewares.auth import authenticated, optional_auth, roles_required


user_bp = Blueprint("users", __name__)


@user_bp.get("/users")
@roles_required("admin", "manager")
def get_users():
    return UserController.list_users()


@user_bp.get("/users/<int:user_id>")
@authenticated
def get_user(user_id):
    return UserController.get_user(user_id)


@user_bp.post("/users")
@optional_auth
def create_user():
    return UserController.create_user()


@user_bp.put("/users/<int:user_id>")
@authenticated
def update_user(user_id):
    return UserController.update_user(user_id)


@user_bp.delete("/users/<int:user_id>")
@roles_required("admin")
def delete_user(user_id):
    return UserController.delete_user(user_id)


@user_bp.get("/users/<int:user_id>/tasks")
@authenticated
def get_user_tasks(user_id):
    return UserController.get_user_tasks(user_id)


@user_bp.post("/login")
def login():
    return UserController.login()
