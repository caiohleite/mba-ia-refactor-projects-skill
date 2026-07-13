from flask import Blueprint, request

from loja.controllers.product_controller import ProductController
from loja.middlewares.auth import require_auth
from loja.views.responses import json_response


product_blueprint = Blueprint("products", __name__)
controller = ProductController()


@product_blueprint.get("/produtos")
def list_products():
    return json_response(controller.list_products())


@product_blueprint.get("/produtos/busca")
def search_products():
    return json_response(controller.search_products(request.args))


@product_blueprint.get("/produtos/<int:id>")
def get_product(id):
    return json_response(controller.get_product(id))


@product_blueprint.post("/produtos")
@require_auth("admin")
def create_product():
    return json_response(controller.create_product(request.get_json(silent=True)))


@product_blueprint.put("/produtos/<int:id>")
@require_auth("admin")
def update_product(id):
    return json_response(controller.update_product(id, request.get_json(silent=True)))


@product_blueprint.delete("/produtos/<int:id>")
@require_auth("admin")
def delete_product(id):
    return json_response(controller.delete_product(id))
