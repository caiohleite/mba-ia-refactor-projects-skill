import logging
import re
import uuid
from datetime import datetime

from exceptions import ValidationError
from schemas.constants import (
    DEFAULT_COLOR,
    DEFAULT_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_TITLE_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
)
from schemas.validators import validate_task_payload
from utils.time import utc_now


logger = logging.getLogger(__name__)


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    return round((part / total) * 100, 2) if total else 0


def validate_email(email):
    return bool(re.fullmatch(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", email or ""))


def sanitize_string(value):
    return value.strip() if value else value


def generate_id():
    return str(uuid.uuid4())


def log_action(action, details=None):
    logger.info(
        "Ação de domínio",
        extra={"action": action, "details": details, "timestamp": str(utc_now())},
    )


def parse_date(date_string):
    for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_string, date_format)
        except (TypeError, ValueError):
            continue
    return None


def is_valid_color(color):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", color or ""))


def process_task_data(data, existing_task=None):
    try:
        return validate_task_payload(data, partial=existing_task is not None), None
    except ValidationError as error:
        return None, error.message


__all__ = [
    "DEFAULT_COLOR",
    "DEFAULT_PRIORITY",
    "MAX_TITLE_LENGTH",
    "MIN_PASSWORD_LENGTH",
    "MIN_TITLE_LENGTH",
    "VALID_ROLES",
    "VALID_STATUSES",
    "calculate_percentage",
    "format_date",
    "generate_id",
    "is_valid_color",
    "log_action",
    "parse_date",
    "process_task_data",
    "sanitize_string",
    "validate_email",
]
