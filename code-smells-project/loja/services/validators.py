from loja.errors import ValidationError


def require_object(data, message="Dados inválidos"):
    if not isinstance(data, dict) or not data:
        raise ValidationError(message)
    return data


def require_non_empty_string(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} é obrigatório")
    return value.strip()


def require_number(value, field_name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name} deve ser numérico")
    return value


def optional_float(value, field_name):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(f"{field_name} deve ser numérico") from error
