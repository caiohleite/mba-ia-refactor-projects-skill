import hmac

from loja.database import get_db
from loja.errors import AuthorizationError
from loja.repositories.admin_repository import AdminRepository


class AdminService:
    def __init__(self, repository=None):
        self.repository = repository or AdminRepository()

    @staticmethod
    def authorize(provided_token, configured_token):
        if not configured_token:
            raise AuthorizationError("Operação administrativa desabilitada")
        if not provided_token or not hmac.compare_digest(provided_token, configured_token):
            raise AuthorizationError("Nao autorizado")

    def reset_database(self, provided_token, configured_token):
        self.authorize(provided_token, configured_token)
        database = get_db()
        try:
            self.repository.reset_database()
            database.commit()
        except Exception:
            database.rollback()
            raise

    @staticmethod
    def reject_arbitrary_query():
        raise AuthorizationError("Execução de SQL arbitrário desabilitada")
