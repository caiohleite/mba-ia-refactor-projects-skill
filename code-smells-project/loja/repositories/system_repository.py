from loja.database import get_db


class SystemRepository:
    def health_counts(self):
        database = get_db()
        return {
            "produtos": database.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
            "usuarios": database.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
            "pedidos": database.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
        }
