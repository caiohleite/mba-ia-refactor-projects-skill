import unittest
from datetime import timedelta
from pathlib import Path

from app import create_app
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.auth_service import AuthService
from utils.time import utc_now


class TaskManagerAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SECRET_KEY": "test-secret-only",
                "AUTH_TOKEN_MAX_AGE": 3600,
            }
        )
        self.context = self.app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()

        self.admin = User(name="Admin", email="admin@example.com", role="admin")
        self.admin.set_password("1234")
        self.manager = User(name="Manager", email="manager@example.com", role="manager")
        self.manager.set_password("1234")
        self.user = User(name="User", email="user@example.com", role="user")
        self.user.set_password("1234")
        self.category = Category(name="Backend", description="Backend", color="#3498db")
        db.session.add_all([self.admin, self.manager, self.user, self.category])
        db.session.flush()
        self.task = Task(
            title="Task existente",
            description="Fixture",
            status="pending",
            priority=2,
            user_id=self.user.id,
            category_id=self.category.id,
            due_date=utc_now() - timedelta(days=1),
        )
        db.session.add(self.task)
        db.session.commit()

        auth = AuthService(self.app.config["SECRET_KEY"])
        self.admin_headers = {"Authorization": f"Bearer {auth.generate_token(self.admin)}"}
        self.manager_headers = {"Authorization": f"Bearer {auth.generate_token(self.manager)}"}
        self.user_headers = {"Authorization": f"Bearer {auth.generate_token(self.user)}"}
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_all_original_endpoint_contracts(self):
        for path in ("/", "/health", "/tasks", f"/tasks/{self.task.id}",
                     "/tasks/search?q=existente", "/tasks/stats", "/categories"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

        login = self.client.post(
            "/login", json={"email": self.admin.email, "password": "1234"}
        )
        self.assertEqual(login.status_code, 200)
        self.assertNotIn("password", login.get_json()["user"])
        admin_headers = {"Authorization": f"Bearer {login.get_json()['token']}"}

        for path in (
            "/users",
            f"/users/{self.admin.id}",
            f"/users/{self.admin.id}/tasks",
            "/reports/summary",
            f"/reports/user/{self.admin.id}",
        ):
            self.assertEqual(self.client.get(path, headers=admin_headers).status_code, 200, path)

        new_user = self.client.post(
            "/users",
            json={"name": "Nova", "email": "nova@example.com", "password": "1234"},
        )
        self.assertEqual(new_user.status_code, 201)
        self.assertNotIn("password", new_user.get_json())
        new_user_id = new_user.get_json()["id"]
        self.assertEqual(
            self.client.put(
                f"/users/{new_user_id}", json={"name": "Nova Pessoa"}, headers=admin_headers
            ).status_code,
            200,
        )

        new_task = self.client.post(
            "/tasks",
            json={
                "title": "Task criada",
                "user_id": self.admin.id,
                "category_id": self.category.id,
            },
            headers=admin_headers,
        )
        self.assertEqual(new_task.status_code, 201)
        new_task_id = new_task.get_json()["id"]
        self.assertEqual(
            self.client.put(
                f"/tasks/{new_task_id}", json={"status": "done"}, headers=admin_headers
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/tasks/{new_task_id}", headers=admin_headers).status_code,
            200,
        )

        new_category = self.client.post(
            "/categories", json={"name": "DevOps"}, headers=admin_headers
        )
        self.assertEqual(new_category.status_code, 201)
        new_category_id = new_category.get_json()["id"]
        self.assertEqual(
            self.client.put(
                f"/categories/{new_category_id}",
                json={"color": "#112233"},
                headers=admin_headers,
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(
                f"/categories/{new_category_id}", headers=admin_headers
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/users/{new_user_id}", headers=admin_headers).status_code,
            200,
        )

    def test_authentication_authorization_and_safe_dtos(self):
        self.assertEqual(self.client.get("/users").status_code, 401)
        self.assertEqual(self.client.post("/tasks", json={"title": "Bloqueada"}).status_code, 401)
        self.assertEqual(self.client.get("/reports/summary").status_code, 401)
        self.assertEqual(
            self.client.post(
                "/categories", json={"name": "Proibida"}, headers=self.user_headers
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get("/reports/summary", headers=self.user_headers).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                f"/reports/user/{self.user.id}", headers=self.user_headers
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(f"/users/{self.admin.id}", headers=self.user_headers).status_code,
            403,
        )
        escalation = self.client.post(
            "/users",
            json={
                "name": "Intruso",
                "email": "intruso@example.com",
                "password": "1234",
                "role": "admin",
            },
        )
        self.assertEqual(escalation.status_code, 403)

        response = self.client.get(f"/users/{self.user.id}", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.get_json())

    def test_validation_errors_and_legacy_password_migration(self):
        invalid_task = self.client.post(
            "/tasks",
            json={"title": "OK", "priority": "invalid"},
            headers=self.admin_headers,
        )
        self.assertEqual(invalid_task.status_code, 400)
        self.assertEqual(
            self.client.post(
                "/users", json={"name": "X", "email": "bad", "password": "1234"}
            ).status_code,
            400,
        )
        self.assertEqual(self.client.get("/tasks/99999").status_code, 404)

        self.user.password = "81dc9bdb52d04dc20036dbd8313ed055"
        db.session.commit()
        response = self.client.post(
            "/login", json={"email": self.user.email, "password": "1234"}
        )
        self.assertEqual(response.status_code, 200)
        db.session.refresh(self.user)
        self.assertFalse(self.user.has_legacy_password())
        self.assertTrue(self.user.check_password("1234"))

    def test_url_map_and_architectural_boundaries(self):
        rules = {
            (method, rule.rule)
            for rule in self.app.url_map.iter_rules()
            if rule.endpoint != "static"
            for method in rule.methods - {"HEAD", "OPTIONS"}
        }
        self.assertEqual(len(rules), 22)

        root = Path(__file__).resolve().parents[1]
        for folder in ("routes", "controllers"):
            for file_path in (root / folder).glob("*.py"):
                source = file_path.read_text(encoding="utf-8")
                self.assertNotIn("from database", source, file_path)
                self.assertNotIn("db.", source, file_path)
                self.assertNotIn(".query", source, file_path)

        source_files = [
            path
            for path in root.rglob("*.py")
            if not {"venv", ".agents", ".codex", "reports", "tests", "__pycache__"}.intersection(path.parts)
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in source_files)
        for forbidden in (
            "super-secret-key-123",
            "senha123",
            "taskmanager@gmail.com",
            "fake-jwt-token",
            "query.get",
            "datetime.utcnow",
            "except:",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertEqual(combined.count("hashlib.md5"), 1)


if __name__ == "__main__":
    unittest.main()
