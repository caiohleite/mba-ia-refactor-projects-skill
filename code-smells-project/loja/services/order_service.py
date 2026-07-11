import logging

from loja.database import get_db
from loja.errors import NotFoundError, ValidationError
from loja.models import VALID_ORDER_STATUSES
from loja.repositories.order_repository import OrderRepository
from loja.repositories.user_repository import UserRepository
from loja.services.validators import require_object


LOGGER = logging.getLogger(__name__)


class OrderService:
    def __init__(self, order_repository=None, user_repository=None):
        self.order_repository = order_repository or OrderRepository()
        self.user_repository = user_repository or UserRepository()

    def create_order(self, data):
        data = require_object(data)
        user_id = data.get("usuario_id")
        items = data.get("itens", [])
        if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError("Usuario ID é obrigatório")
        if not isinstance(items, list) or not items:
            raise ValidationError("Pedido deve ter pelo menos 1 item")
        if self.user_repository.get_by_id(user_id) is None:
            raise ValidationError("Usuário não encontrado")

        quantities = self._normalize_items(items)
        products = self.order_repository.get_products_by_ids(quantities)
        for product_id, quantity in quantities.items():
            product = products.get(product_id)
            if product is None:
                raise ValidationError(f"Produto {product_id} não encontrado")
            if product.estoque < quantity:
                raise ValidationError(f"Estoque insuficiente para {product.nome}")

        total = sum(products[product_id].preco * quantity for product_id, quantity in quantities.items())
        database = get_db()
        try:
            database.execute("BEGIN")
            order_id = self.order_repository.create(user_id, total)
            for product_id, quantity in quantities.items():
                product = products[product_id]
                if not self.order_repository.decrease_stock(product_id, quantity):
                    raise ValidationError(f"Estoque insuficiente para {product.nome}")
                self.order_repository.add_item(order_id, product_id, quantity, product.preco)
            database.commit()
        except Exception:
            database.rollback()
            raise

        LOGGER.info("Pedido %s criado para usuario %s", order_id, user_id)
        return {"pedido_id": order_id, "total": total}

    def list_orders(self):
        return [order.to_dict() for order in self.order_repository.list_all()]

    def list_user_orders(self, user_id):
        return [order.to_dict() for order in self.order_repository.list_by_user(user_id)]

    def update_status(self, order_id, new_status):
        if new_status not in VALID_ORDER_STATUSES:
            raise ValidationError("Status inválido")
        current_status = self.order_repository.get_status(order_id)
        if current_status is None:
            raise NotFoundError("Pedido não encontrado")
        if current_status == new_status:
            return

        database = get_db()
        try:
            database.execute("BEGIN")
            items = self.order_repository.get_items(order_id)
            if new_status == "cancelado":
                for item in items:
                    self.order_repository.increase_stock(item["produto_id"], item["quantidade"])
            elif current_status == "cancelado":
                for item in items:
                    if not self.order_repository.decrease_stock(item["produto_id"], item["quantidade"]):
                        raise ValidationError("Estoque insuficiente para reativar o pedido")
            self.order_repository.update_status(order_id, new_status)
            database.commit()
        except Exception:
            database.rollback()
            raise

        LOGGER.info("Status do pedido %s alterado para %s", order_id, new_status)

    @staticmethod
    def _normalize_items(items):
        quantities = {}
        for item in items:
            if not isinstance(item, dict):
                raise ValidationError("Item do pedido inválido")
            product_id = item.get("produto_id")
            quantity = item.get("quantidade")
            if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
                raise ValidationError("Produto ID inválido")
            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
                raise ValidationError("Quantidade deve ser um inteiro positivo")
            quantities[product_id] = quantities.get(product_id, 0) + quantity
        return quantities
