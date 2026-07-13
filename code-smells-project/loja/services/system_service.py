from loja.repositories.system_repository import SystemRepository


class SystemService:
    def __init__(self, repository=None):
        self.repository = repository or SystemRepository()

    def health(self, environment):
        return {
            "status": "ok",
            "database": "connected",
            "counts": self.repository.health_counts(),
            "versao": "1.0.0",
            "ambiente": environment,
        }
