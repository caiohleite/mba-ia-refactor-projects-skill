from datetime import datetime, timezone


def utc_now():
    """Retorna UTC sem tzinfo para compatibilidade com as colunas SQLite atuais."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

