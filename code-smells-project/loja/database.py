import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


PRODUCT_SEED = (
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
)

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL DEFAULT '',
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'cliente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pendente',
    total REAL NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_pedidos_usuario_id ON pedidos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido_id ON itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_produto_id ON itens_pedido(produto_id);
"""


def get_db():
    if "db" not in g:
        database_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(database_path, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_database():
    database = get_db()
    existing_tables = database.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN (?, ?, ?, ?)",
        ("produtos", "usuarios", "pedidos", "itens_pedido"),
    ).fetchall()
    if existing_tables and not _has_required_constraints(database):
        _migrate_legacy_schema(database)
    else:
        database.executescript(SCHEMA)
    database.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    database.commit()


def _has_required_constraints(database):
    user_indexes = database.execute("PRAGMA index_list('usuarios')").fetchall()
    order_foreign_keys = database.execute("PRAGMA foreign_key_list('pedidos')").fetchall()
    item_foreign_keys = database.execute("PRAGMA foreign_key_list('itens_pedido')").fetchall()
    has_unique_email = any(index[2] for index in user_indexes)
    return has_unique_email and bool(order_foreign_keys) and len(item_foreign_keys) >= 2


def _migrate_legacy_schema(database):
    migration = f"""
    PRAGMA foreign_keys = OFF;
    BEGIN IMMEDIATE;
    ALTER TABLE produtos RENAME TO legacy_produtos;
    ALTER TABLE usuarios RENAME TO legacy_usuarios;
    ALTER TABLE pedidos RENAME TO legacy_pedidos;
    ALTER TABLE itens_pedido RENAME TO legacy_itens_pedido;

    {SCHEMA}

    INSERT INTO produtos
        (id, nome, descricao, preco, estoque, categoria, ativo, criado_em)
    SELECT id, nome, descricao, preco, estoque, categoria, ativo, criado_em
    FROM legacy_produtos;

    INSERT INTO usuarios (id, nome, email, senha, tipo, criado_em)
    SELECT id, nome, email, senha, tipo, criado_em
    FROM legacy_usuarios;

    INSERT INTO pedidos (id, usuario_id, status, total, criado_em)
    SELECT id, usuario_id, status, total, criado_em
    FROM legacy_pedidos;

    INSERT INTO itens_pedido
        (id, pedido_id, produto_id, quantidade, preco_unitario)
    SELECT
        item.id,
        item.pedido_id,
        product.id,
        item.quantidade,
        item.preco_unitario
    FROM legacy_itens_pedido AS item
    LEFT JOIN produtos AS product ON product.id = item.produto_id;

    DROP TABLE legacy_itens_pedido;
    DROP TABLE legacy_pedidos;
    DROP TABLE legacy_produtos;
    DROP TABLE legacy_usuarios;
    """
    try:
        database.executescript(migration)
        violations = database.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise sqlite3.IntegrityError(f"Migração produziria {len(violations)} violações de FK")
        database.commit()
    except Exception:
        if database.in_transaction:
            database.rollback()
        raise
    finally:
        database.execute("PRAGMA foreign_keys = ON")


def seed_database():
    database = get_db()

    product_count = database.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    if product_count == 0:
        database.executemany(
            """
            INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
            PRODUCT_SEED,
        )

    admin_email = current_app.config.get("SEED_ADMIN_EMAIL")
    admin_password = current_app.config.get("SEED_ADMIN_PASSWORD")
    if bool(admin_email) != bool(admin_password):
        raise RuntimeError("SEED_ADMIN_EMAIL e SEED_ADMIN_PASSWORD devem ser configurados juntos")
    if admin_email:
        existing_admin = database.execute(
            "SELECT id FROM usuarios WHERE email = ? LIMIT 1",
            (admin_email,),
        ).fetchone()
        if existing_admin is None:
            database.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (
                    current_app.config["SEED_ADMIN_NAME"],
                    admin_email,
                    generate_password_hash(admin_password),
                    "admin",
                ),
            )

    database.commit()


@click.command("init-db")
def init_database_command():
    """Create or update the database schema."""
    init_database()
    click.echo("Banco de dados inicializado.")


@click.command("seed-db")
def seed_database_command():
    """Load explicitly configured development/demo data."""
    init_database()
    seed_database()
    click.echo("Dados de seed carregados.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_database_command)
    app.cli.add_command(seed_database_command)
