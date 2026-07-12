import re
from datetime import datetime

from exceptions import ValidationError
from schemas.constants import (
    DEFAULT_COLOR,
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
)


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")


def require_payload(data):
    if not isinstance(data, dict) or not data:
        raise ValidationError("Dados inválidos")
    return data


def _validate_title(title, required):
    if title is None:
        if required:
            raise ValidationError("Título é obrigatório")
        return None
    if not isinstance(title, str):
        raise ValidationError("Título inválido")
    title = title.strip()
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")
    return title


def _parse_due_date(value):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD") from error


def _normalize_tags(tags):
    if tags is None:
        return None
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise ValidationError("Tags inválidas")
        return ",".join(tags)
    if isinstance(tags, str):
        return tags
    raise ValidationError("Tags inválidas")


def validate_task_payload(data, partial=False):
    require_payload(data)
    cleaned = {}

    if not partial or "title" in data:
        cleaned["title"] = _validate_title(data.get("title"), required=not partial)
    if "description" in data or not partial:
        cleaned["description"] = data.get("description", "")
    if "status" in data or not partial:
        status = data.get("status", VALID_STATUSES[0])
        if status not in VALID_STATUSES:
            raise ValidationError("Status inválido")
        cleaned["status"] = status
    if "priority" in data or not partial:
        try:
            priority = int(data.get("priority", DEFAULT_PRIORITY))
        except (TypeError, ValueError) as error:
            raise ValidationError("Prioridade inválida") from error
        if not MIN_PRIORITY <= priority <= MAX_PRIORITY:
            raise ValidationError("Prioridade deve ser entre 1 e 5")
        cleaned["priority"] = priority
    for field in ("user_id", "category_id"):
        if field in data or not partial:
            cleaned[field] = data.get(field)
    if "due_date" in data:
        cleaned["due_date"] = _parse_due_date(data["due_date"])
    if "tags" in data:
        cleaned["tags"] = _normalize_tags(data["tags"])
    return cleaned


def validate_user_payload(data, partial=False):
    require_payload(data)
    cleaned = {}

    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Nome é obrigatório")
        cleaned["name"] = name.strip()
    if not partial or "email" in data:
        email = data.get("email")
        if not email:
            raise ValidationError("Email é obrigatório")
        if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email):
            raise ValidationError("Email inválido")
        cleaned["email"] = email
    if not partial or "password" in data:
        password = data.get("password")
        if not password:
            raise ValidationError("Senha é obrigatória")
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha deve ter no mínimo 4 caracteres")
        cleaned["password"] = password
    if "role" in data or not partial:
        role = data.get("role", "user")
        if role not in VALID_ROLES:
            raise ValidationError("Role inválido")
        cleaned["role"] = role
    if "active" in data:
        if not isinstance(data["active"], bool):
            raise ValidationError("Active deve ser booleano")
        cleaned["active"] = data["active"]
    return cleaned


def validate_category_payload(data, partial=False):
    require_payload(data)
    cleaned = {}
    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Nome é obrigatório")
        cleaned["name"] = name.strip()
    if "description" in data or not partial:
        cleaned["description"] = data.get("description", "")
    if "color" in data or not partial:
        color = data.get("color", DEFAULT_COLOR)
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ValidationError("Cor inválida")
        cleaned["color"] = color
    return cleaned


def parse_optional_int(value, field_name):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"{field_name} inválido") from error
