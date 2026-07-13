import os
import sqlite3
import tempfile
import unittest

from loja import create_app
from loja.database import get_db
from loja.middlewares.auth import require_auth
from loja.services.report_service import ReportService


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temporary_directory.name, "test.db")
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-only-secret-key",
                "DATABASE": self.database_path,
                "ADMIN_TOKEN": "test-admin-token",
                "AUTO_INIT_DATABASE": True,
                "SEED_DATA": True,
                "SEED_ADMIN_NAME": "Test Admin",
                "SEED_ADMIN_EMAIL": "admin@test.local",
                "SEED_ADMIN_PASSWORD": "test-admin-password",
                "ENVIRONMENT": "test",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _login_admin(self):
        response = self.client.post(
            "/login",
            json={"email": "admin@test.local", "senha": "test-admin-password"},
        )
        self.assertEqual(200, response.status_code)
        return response

    def test_exact_route_contract(self):
        expected = {
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/pedidos"),
            ("GET", "/pedidos/usuario/<int:usuario_id>"),
            ("GET", "/produtos"),
            ("GET", "/produtos/<int:id>"),
            ("GET", "/produtos/busca"),
            ("GET", "/relatorios/vendas"),
            ("GET", "/usuarios"),
            ("GET", "/usuarios/<int:id>"),
            ("POST", "/admin/query"),
            ("POST", "/admin/reset-db"),
            ("POST", "/login"),
            ("POST", "/pedidos"),
            ("POST", "/produtos"),
            ("POST", "/usuarios"),
            ("PUT", "/pedidos/<int:pedido_id>/status"),
            ("PUT", "/produtos/<int:id>"),
            ("DELETE", "/produtos/<int:id>"),
        }
        actual = {
            (method, rule.rule)
            for rule in self.app.url_map.iter_rules()
            if rule.endpoint != "static"
            for method in rule.methods - {"HEAD", "OPTIONS"}
        }
        self.assertEqual(expected, actual)

    def test_root_and_sanitized_health(self):
        root = self.client.get("/")
        self.assertEqual(200, root.status_code)
        self.assertEqual("1.0.0", root.get_json()["versao"])

        health = self.client.get("/health")
        self.assertEqual(200, health.status_code)
        payload = health.get_json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("test", payload["ambiente"])
        self.assertFalse({"secret_key", "db_path", "debug"} & set(payload))
        cross_origin = self.client.get("/", headers={"Origin": "https://untrusted.invalid"})
        self.assertNotIn("Access-Control-Allow-Origin", cross_origin.headers)

        cors_app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "cors-test-key",
                "CORS_ORIGINS": ("https://trusted.example",),
                "AUTO_INIT_DATABASE": False,
            }
        )
        trusted_origin = cors_app.test_client().get(
            "/",
            headers={"Origin": "https://trusted.example"},
        )
        self.assertEqual(
            "https://trusted.example",
            trusted_origin.headers["Access-Control-Allow-Origin"],
        )

    def test_auth_middleware_session_and_roles(self):
        @self.app.get("/_test/admin-only")
        @require_auth("admin")
        def admin_only():
            return {"sucesso": True}

        self.assertEqual(401, self.client.get("/_test/admin-only").status_code)
        admin_login = self.client.post(
            "/login",
            json={"email": "admin@test.local", "senha": "test-admin-password"},
        )
        self.assertEqual(200, admin_login.status_code)
        session_cookie = admin_login.headers["Set-Cookie"]
        self.assertIn("HttpOnly", session_cookie)
        self.assertIn("SameSite=Lax", session_cookie)
        with self.client.session_transaction() as current_session:
            self.assertEqual(
                {"id": 1, "tipo": "admin"},
                current_session["principal"],
            )
        self.assertEqual(200, self.client.get("/_test/admin-only").status_code)

        created = self.client.post(
            "/usuarios",
            json={"nome": "Cliente", "email": "cliente@test.local", "senha": "senha-forte"},
        )
        self.assertEqual(201, created.status_code)
        client_login = self.client.post(
            "/login",
            json={"email": "cliente@test.local", "senha": "senha-forte"},
        )
        self.assertEqual(200, client_login.status_code)
        self.assertEqual(403, self.client.get("/_test/admin-only").status_code)

    def test_authorization_and_order_ownership(self):
        self.assertEqual(401, self.client.get("/usuarios").status_code)
        self.assertEqual(401, self.client.get("/pedidos").status_code)
        self.assertEqual(
            401,
            self.client.post(
                "/produtos",
                json={"nome": "Bloqueado", "preco": 1, "estoque": 1},
            ).status_code,
        )

        first = self.client.post(
            "/usuarios",
            json={"nome": "Primeiro", "email": "first@test.local", "senha": "senha-forte"},
        ).get_json()["dados"]["id"]
        second = self.client.post(
            "/usuarios",
            json={"nome": "Segundo", "email": "second@test.local", "senha": "senha-forte"},
        ).get_json()["dados"]["id"]
        self.client.post(
            "/login",
            json={"email": "first@test.local", "senha": "senha-forte"},
        )

        self.assertEqual(200, self.client.get(f"/usuarios/{first}").status_code)
        self.assertEqual(403, self.client.get(f"/usuarios/{second}").status_code)
        self.assertEqual(403, self.client.get("/usuarios").status_code)
        self.assertEqual(403, self.client.get("/pedidos").status_code)
        self.assertEqual(403, self.client.get("/relatorios/vendas").status_code)
        self.assertEqual(
            403,
            self.client.post(
                "/produtos",
                json={"nome": "Bloqueado", "preco": 1, "estoque": 1},
            ).status_code,
        )

        own_order = self.client.post(
            "/pedidos",
            json={"usuario_id": first, "itens": [{"produto_id": 1, "quantidade": 1}]},
        )
        self.assertEqual(201, own_order.status_code)
        order_id = own_order.get_json()["dados"]["pedido_id"]
        self.assertEqual(200, self.client.get(f"/pedidos/usuario/{first}").status_code)
        self.assertEqual(403, self.client.get(f"/pedidos/usuario/{second}").status_code)
        self.assertEqual(
            403,
            self.client.post(
                "/pedidos",
                json={"usuario_id": second, "itens": [{"produto_id": 1, "quantidade": 1}]},
            ).status_code,
        )
        self.assertEqual(
            403,
            self.client.put(
                f"/pedidos/{order_id}/status",
                json={"status": "aprovado"},
            ).status_code,
        )

        self._login_admin()
        self.assertEqual(200, self.client.get("/usuarios").status_code)
        self.assertEqual(200, self.client.get("/pedidos").status_code)
        self.assertEqual(200, self.client.get("/relatorios/vendas").status_code)
        self.assertEqual(
            200,
            self.client.put(
                f"/pedidos/{order_id}/status",
                json={"status": "aprovado"},
            ).status_code,
        )

    def test_product_crud_and_safe_search(self):
        self._login_admin()
        listed = self.client.get("/produtos")
        self.assertEqual(200, listed.status_code)
        self.assertEqual(10, len(listed.get_json()["dados"]))
        self.assertEqual(200, self.client.get("/produtos/1").status_code)

        created = self.client.post(
            "/produtos",
            json={
                "nome": "Produto ' seguro",
                "descricao": "teste",
                "preco": 15.5,
                "estoque": 4,
                "categoria": "geral",
            },
        )
        self.assertEqual(201, created.status_code)
        product_id = created.get_json()["dados"]["id"]

        updated = self.client.put(
            f"/produtos/{product_id}",
            json={
                "nome": "Produto atualizado",
                "descricao": "teste 2",
                "preco": 20,
                "estoque": 3,
                "categoria": "livros",
            },
        )
        self.assertEqual(200, updated.status_code)
        search = self.client.get("/produtos/busca", query_string={"q": "atualizado"})
        self.assertEqual(1, search.get_json()["total"])

        injection = self.client.get(
            "/produtos/busca",
            query_string={"q": "%' OR 1=1 --"},
        )
        self.assertEqual(200, injection.status_code)
        self.assertEqual(0, injection.get_json()["total"])

        self.assertEqual(200, self.client.delete(f"/produtos/{product_id}").status_code)
        self.assertEqual(404, self.client.get(f"/produtos/{product_id}").status_code)
        with self.app.app_context():
            inactive = get_db().execute(
                "SELECT ativo FROM produtos WHERE id = ?",
                (product_id,),
            ).fetchone()
        self.assertEqual(0, inactive["ativo"])

    def test_user_contract_hash_and_login_security(self):
        self._login_admin()
        listed = self.client.get("/usuarios")
        self.assertEqual(200, listed.status_code)
        for user in listed.get_json()["dados"]:
            self.assertNotIn("senha", user)
            self.assertNotIn("password_hash", user)

        found = self.client.get("/usuarios/1")
        self.assertEqual(200, found.status_code)
        self.assertNotIn("senha", found.get_json()["dados"])

        created = self.client.post(
            "/usuarios",
            json={"nome": "Novo Usuario", "email": "novo@example.com", "senha": "senha123"},
        )
        self.assertEqual(201, created.status_code)
        with self.app.app_context():
            stored = get_db().execute(
                "SELECT senha FROM usuarios WHERE email = ?",
                ("novo@example.com",),
            ).fetchone()["senha"]
        self.assertNotEqual("senha123", stored)
        self.assertIn("$", stored)

        duplicate = self.client.post(
            "/usuarios",
            json={"nome": "Duplicado", "email": "NOVO@EXAMPLE.COM", "senha": "outra-senha"},
        )
        self.assertEqual(409, duplicate.status_code)

        login = self.client.post(
            "/login",
            json={"email": "novo@example.com", "senha": "senha123"},
        )
        self.assertEqual(200, login.status_code)
        injection = self.client.post(
            "/login",
            json={"email": "' OR 1=1 --", "senha": "irrelevante"},
        )
        self.assertEqual(401, injection.status_code)

    def test_database_constraints_and_legacy_migration(self):
        with self.app.app_context():
            database = get_db()
            self.assertEqual(1, database.execute("PRAGMA user_version").fetchone()[0])
            self.assertTrue(database.execute("PRAGMA foreign_key_list('pedidos')").fetchall())
            self.assertEqual(
                2,
                len(database.execute("PRAGMA foreign_key_list('itens_pedido')").fetchall()),
            )
            with self.assertRaises(sqlite3.IntegrityError):
                database.execute(
                    "INSERT INTO pedidos (usuario_id, total) VALUES (?, ?)",
                    (99999, 10),
                )
            database.rollback()

        legacy_path = os.path.join(self.temporary_directory.name, "legacy.db")
        legacy = sqlite3.connect(legacy_path)
        legacy.executescript(
            """
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL DEFAULT '',
                preco REAL NOT NULL,
                estoque INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'cliente',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                total REAL NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL
            );
            INSERT INTO produtos
                (id, nome, descricao, preco, estoque, categoria)
            VALUES (1, 'Legado', '', 10, 2, 'geral');
            INSERT INTO usuarios (id, nome, email, senha, tipo)
            VALUES (1, 'Legado', 'legacy@example.com', 'hash-legado', 'cliente');
            INSERT INTO pedidos (id, usuario_id, total) VALUES (1, 1, 10);
            INSERT INTO itens_pedido
                (id, pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (1, 1, 1, 1, 10);
            """
        )
        legacy.close()

        migrated_app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "migration-test-key",
                "DATABASE": legacy_path,
                "AUTO_INIT_DATABASE": True,
                "SEED_DATA": False,
            }
        )
        with migrated_app.app_context():
            database = get_db()
            self.assertEqual(1, database.execute("PRAGMA user_version").fetchone()[0])
            self.assertEqual(
                "legacy@example.com",
                database.execute("SELECT email FROM usuarios WHERE id = 1").fetchone()[0],
            )
            self.assertEqual([], database.execute("PRAGMA foreign_key_check").fetchall())

    def test_order_stock_status_and_report_contract(self):
        self._login_admin()
        initial_stock = self.client.get("/produtos/1").get_json()["dados"]["estoque"]
        created = self.client.post(
            "/pedidos",
            json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 2}]},
        )
        self.assertEqual(201, created.status_code)
        order_id = created.get_json()["dados"]["pedido_id"]
        self.assertEqual(
            initial_stock - 2,
            self.client.get("/produtos/1").get_json()["dados"]["estoque"],
        )

        self.assertEqual(200, self.client.get("/pedidos").status_code)
        user_orders = self.client.get("/pedidos/usuario/1")
        self.assertEqual(200, user_orders.status_code)
        self.assertEqual(order_id, user_orders.get_json()["dados"][0]["id"])

        cancelled = self.client.put(
            f"/pedidos/{order_id}/status",
            json={"status": "cancelado"},
        )
        self.assertEqual(200, cancelled.status_code)
        self.assertEqual(
            initial_stock,
            self.client.get("/produtos/1").get_json()["dados"]["estoque"],
        )

        report = self.client.get("/relatorios/vendas")
        self.assertEqual(200, report.status_code)
        self.assertEqual(1, report.get_json()["dados"]["pedidos_cancelados"])

        self.assertEqual(200, self.client.delete("/produtos/1").status_code)
        historical_order = self.client.get("/pedidos").get_json()["dados"][0]
        self.assertEqual("Notebook Gamer", historical_order["itens"][0]["produto_nome"])
        unavailable = self.client.post(
            "/pedidos",
            json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 1}]},
        )
        self.assertEqual(400, unavailable.status_code)

    def test_discount_policy_boundaries(self):
        cases = (
            (1_000, 0),
            (1_000.01, 20.0002),
            (5_000, 100),
            (5_000.01, 250.0005),
            (10_000, 500),
            (10_000.01, 1_000.001),
        )
        for revenue, expected_discount in cases:
            with self.subTest(revenue=revenue):
                self.assertAlmostEqual(
                    expected_discount,
                    ReportService._calculate_discount(revenue),
                )

    def test_admin_endpoints_fail_closed(self):
        self._login_admin()
        before = self.client.get("/usuarios").get_json()["dados"]
        query = self.client.post("/admin/query", json={"sql": "DELETE FROM usuarios"})
        self.assertEqual(403, query.status_code)
        self.assertEqual(before, self.client.get("/usuarios").get_json()["dados"])

        self.assertEqual(403, self.client.post("/admin/reset-db").status_code)
        self.assertEqual(
            403,
            self.client.post(
                "/admin/reset-db",
                headers={"X-Admin-Token": "wrong-token"},
            ).status_code,
        )
        authorized = self.client.post(
            "/admin/reset-db",
            headers={"X-Admin-Token": "test-admin-token"},
        )
        self.assertEqual(200, authorized.status_code)
        self.assertEqual([], self.client.get("/usuarios").get_json()["dados"])

    def test_validation_and_unexpected_errors_are_sanitized(self):
        @self.app.get("/_test/unexpected")
        def unexpected_error():
            raise sqlite3.DatabaseError("internal database detail")

        self._login_admin()
        invalid = self.client.post(
            "/pedidos",
            json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": -1}]},
        )
        self.assertEqual(400, invalid.status_code)
        self.assertNotIn("traceback", str(invalid.get_json()).lower())

        unexpected = self.client.get("/_test/unexpected")
        self.assertEqual(500, unexpected.status_code)
        self.assertEqual("Erro interno do servidor", unexpected.get_json()["erro"])
        self.assertNotIn("database detail", str(unexpected.get_json()).lower())


if __name__ == "__main__":
    unittest.main()
