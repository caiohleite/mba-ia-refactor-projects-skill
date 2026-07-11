import os
import sqlite3
import tempfile
import unittest

from loja import create_app
from loja.database import get_db


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temporary_directory.name, "test.db")
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.database_path,
                "ADMIN_TOKEN": "test-admin-token",
                "ENVIRONMENT": "test",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

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

    def test_product_crud_and_safe_search(self):
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

    def test_user_contract_hash_and_login_security(self):
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

    def test_order_stock_status_and_report_contract(self):
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

    def test_admin_endpoints_fail_closed(self):
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
