from loja.database import get_db
from loja.models import Product


class ProductRepository:
    def list_all(self):
        rows = get_db().execute("SELECT * FROM produtos ORDER BY id").fetchall()
        return [Product.from_row(row) for row in rows]

    def get_by_id(self, product_id):
        row = get_db().execute(
            "SELECT * FROM produtos WHERE id = ?",
            (product_id,),
        ).fetchone()
        return Product.from_row(row) if row else None

    def create(self, nome, descricao, preco, estoque, categoria):
        cursor = get_db().execute(
            """
            INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nome, descricao, preco, estoque, categoria),
        )
        return cursor.lastrowid

    def update(self, product_id, nome, descricao, preco, estoque, categoria):
        cursor = get_db().execute(
            """
            UPDATE produtos
            SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
            WHERE id = ?
            """,
            (nome, descricao, preco, estoque, categoria, product_id),
        )
        return cursor.rowcount > 0

    def delete(self, product_id):
        cursor = get_db().execute(
            "DELETE FROM produtos WHERE id = ?",
            (product_id,),
        )
        return cursor.rowcount > 0

    def search(self, term="", category=None, min_price=None, max_price=None):
        clauses = ["1 = 1"]
        parameters = []

        if term:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            pattern = f"%{term}%"
            parameters.extend((pattern, pattern))
        if category:
            clauses.append("categoria = ?")
            parameters.append(category)
        if min_price is not None:
            clauses.append("preco >= ?")
            parameters.append(min_price)
        if max_price is not None:
            clauses.append("preco <= ?")
            parameters.append(max_price)

        query = "SELECT * FROM produtos WHERE " + " AND ".join(clauses) + " ORDER BY id"
        rows = get_db().execute(query, parameters).fetchall()
        return [Product.from_row(row) for row in rows]
