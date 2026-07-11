from flask import Blueprint, request

from loja.controllers.user_controller import UserController
from loja.middlewares.auth import login_user, require_auth
from loja.views.responses import json_response


user_blueprint = Blueprint("users", __name__)
controller = UserController()


@user_blueprint.get("/usuarios")
@require_auth("admin")
def list_users():
    return json_response(controller.list_users())


@user_blueprint.get("/usuarios/<int:id>")
@require_auth("admin", "cliente", owner_arg="id")
def get_user(id):
    return json_response(controller.get_user(id))


@user_blueprint.post("/usuarios")
def create_user():
    return json_response(controller.create_user(request.get_json(silent=True)))


@user_blueprint.post("/login")
def login():
    result = controller.login(request.get_json(silent=True))
    login_user(result[0]["dados"])
    return json_response(result)
