from flask import Blueprint, current_app, request

from loja.controllers.system_controller import SystemController
from loja.views.responses import json_response


system_blueprint = Blueprint("system", __name__)
controller = SystemController()


@system_blueprint.get("/")
def index():
    return json_response(controller.index())


@system_blueprint.get("/health")
def health():
    return json_response(controller.health(current_app.config["ENVIRONMENT"]))


@system_blueprint.post("/admin/reset-db")
def reset_database():
    return json_response(
        controller.reset_database(
            request.headers.get("X-Admin-Token"),
            current_app.config.get("ADMIN_TOKEN"),
        )
    )


@system_blueprint.post("/admin/query")
def reject_query():
    return json_response(controller.reject_query())
