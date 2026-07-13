from loja.database import get_db
from loja.models import User


class UserRepository:
    def list_all(self):
        rows = get_db().execute("SELECT * FROM usuarios ORDER BY id").fetchall()
        return [User.from_row(row) for row in rows]

    def get_by_id(self, user_id):
        row = get_db().execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (user_id,),
        ).fetchone()
        return User.from_row(row) if row else None

    def get_by_email(self, email):
        row = get_db().execute(
            "SELECT * FROM usuarios WHERE email = ? ORDER BY id LIMIT 1",
            (email,),
        ).fetchone()
        return User.from_row(row) if row else None

    def create(self, nome, email, password_hash, user_type="cliente"):
        cursor = get_db().execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, password_hash, user_type),
        )
        return cursor.lastrowid

    def update_password(self, user_id, password_hash):
        get_db().execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (password_hash, user_id),
        )
