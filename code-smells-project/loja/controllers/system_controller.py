from loja.services.admin_service import AdminService
from loja.services.system_service import SystemService


class SystemController:
    def __init__(self, system_service=None, admin_service=None):
        self.system_service = system_service or SystemService()
        self.admin_service = admin_service or AdminService()

    @staticmethod
    def index():
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }, 200

    def health(self, environment):
        return self.system_service.health(environment), 200

    def reset_database(self, provided_token, configured_token):
        self.admin_service.reset_database(provided_token, configured_token)
        return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200

    def reject_query(self):
        self.admin_service.reject_arbitrary_query()
