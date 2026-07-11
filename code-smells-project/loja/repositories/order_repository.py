from loja.database import get_db
from loja.models import Order, OrderItem, Product


class OrderRepository:
    def get_products_by_ids(self, product_ids):
        if not product_ids:
            return {}
        placeholders = ", ".join("?" for _product_id in product_ids)
        rows = get_db().execute(
            f"SELECT * FROM produtos WHERE id IN ({placeholders})",
            tuple(product_ids),
        ).fetchall()
        return {row["id"]: Product.from_row(row) for row in rows}

    def create(self, user_id, total):
        cursor = get_db().execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (user_id, total),
        )
        return cursor.lastrowid

    def add_item(self, order_id, product_id, quantity, unit_price):
        get_db().execute(
            """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, product_id, quantity, unit_price),
        )

    def decrease_stock(self, product_id, quantity):
        cursor = get_db().execute(
            """
            UPDATE produtos
            SET estoque = estoque - ?
            WHERE id = ? AND estoque >= ?
            """,
            (quantity, product_id, quantity),
        )
        return cursor.rowcount > 0

    def increase_stock(self, product_id, quantity):
        get_db().execute(
            "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
            (quantity, product_id),
        )

    def get_status(self, order_id):
        row = get_db().execute(
            "SELECT status FROM pedidos WHERE id = ?",
            (order_id,),
        ).fetchone()
        return row["status"] if row else None

    def get_items(self, order_id):
        return get_db().execute(
            """
            SELECT produto_id, quantidade
            FROM itens_pedido
            WHERE pedido_id = ?
            ORDER BY id
            """,
            (order_id,),
        ).fetchall()

    def update_status(self, order_id, status):
        cursor = get_db().execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (status, order_id),
        )
        return cursor.rowcount > 0

    def list_all(self):
        return self._list_orders()

    def list_by_user(self, user_id):
        return self._list_orders(user_id)

    def _list_orders(self, user_id=None):
        where = "WHERE p.usuario_id = ?" if user_id is not None else ""
        parameters = (user_id,) if user_id is not None else ()
        rows = get_db().execute(
            f"""
            SELECT
                p.id AS pedido_id,
                p.usuario_id,
                p.status,
                p.total,
                p.criado_em,
                i.produto_id,
                i.quantidade,
                i.preco_unitario,
                pr.nome AS produto_nome
            FROM pedidos AS p
            LEFT JOIN itens_pedido AS i ON i.pedido_id = p.id
            LEFT JOIN produtos AS pr ON pr.id = i.produto_id
            {where}
            ORDER BY p.id, i.id
            """,
            parameters,
        ).fetchall()

        orders = {}
        for row in rows:
            order = orders.setdefault(
                row["pedido_id"],
                Order(
                    id=row["pedido_id"],
                    usuario_id=row["usuario_id"],
                    status=row["status"],
                    total=row["total"],
                    criado_em=row["criado_em"],
                ),
            )
            if row["produto_id"] is not None:
                order.itens.append(
                    OrderItem(
                        produto_id=row["produto_id"],
                        produto_nome=row["produto_nome"] or "Desconhecido",
                        quantidade=row["quantidade"],
                        preco_unitario=row["preco_unitario"],
                    )
                )
        return list(orders.values())
