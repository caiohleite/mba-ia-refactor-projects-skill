from loja.database import get_db


class AdminRepository:
    def reset_database(self):
        database = get_db()
        database.execute("DELETE FROM itens_pedido")
        database.execute("DELETE FROM pedidos")
        database.execute("DELETE FROM produtos")
        database.execute("DELETE FROM usuarios")
