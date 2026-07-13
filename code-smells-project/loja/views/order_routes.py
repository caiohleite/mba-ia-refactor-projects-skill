from flask import Blueprint, g, request

from loja.controllers.order_controller import OrderController
from loja.controllers.report_controller import ReportController
from loja.middlewares.auth import require_auth
from loja.views.responses import json_response


order_blueprint = Blueprint("orders", __name__)
order_controller = OrderController()
report_controller = ReportController()


@order_blueprint.post("/pedidos")
@require_auth("admin", "cliente")
def create_order():
    return json_response(
        order_controller.create_order(request.get_json(silent=True), g.current_user)
    )


@order_blueprint.get("/pedidos")
@require_auth("admin")
def list_orders():
    return json_response(order_controller.list_orders())


@order_blueprint.get("/pedidos/usuario/<int:usuario_id>")
@require_auth("admin", "cliente", owner_arg="usuario_id")
def list_user_orders(usuario_id):
    return json_response(order_controller.list_user_orders(usuario_id))


@order_blueprint.put("/pedidos/<int:pedido_id>/status")
@require_auth("admin")
def update_order_status(pedido_id):
    return json_response(
        order_controller.update_status(pedido_id, request.get_json(silent=True))
    )


@order_blueprint.get("/relatorios/vendas")
@require_auth("admin")
def sales_report():
    return json_response(report_controller.sales_report())
