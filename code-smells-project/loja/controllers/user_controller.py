from loja.services.user_service import UserService


class UserController:
    def __init__(self, service=None):
        self.service = service or UserService()

    def list_users(self):
        return {"dados": self.service.list_users(), "sucesso": True}, 200

    def get_user(self, user_id):
        return {"dados": self.service.get_user(user_id), "sucesso": True}, 200

    def create_user(self, data):
        user_id = self.service.create_user(data)
        return {"dados": {"id": user_id}, "sucesso": True}, 201

    def login(self, data):
        user = self.service.login(data)
        return {"dados": user, "sucesso": True, "mensagem": "Login OK"}, 200
