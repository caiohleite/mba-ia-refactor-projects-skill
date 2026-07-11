from loja.services.order_service import OrderService


class OrderController:
    def __init__(self, service=None):
        self.service = service or OrderService()

    def create_order(self, data):
        result = self.service.create_order(data)
        return {
            "dados": result,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }, 201

    def list_orders(self):
        return {"dados": self.service.list_orders(), "sucesso": True}, 200

    def list_user_orders(self, user_id):
        return {"dados": self.service.list_user_orders(user_id), "sucesso": True}, 200

    def update_status(self, order_id, data):
        status = data.get("status", "") if isinstance(data, dict) else ""
        self.service.update_status(order_id, status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200
