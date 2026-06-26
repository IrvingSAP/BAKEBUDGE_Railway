"""Utilidades compartidas para errores de formularios HTML (modal + campos)."""

from decimal import Decimal, InvalidOperation

FIELD_LABELS = {
    "nombre": "Nombre",
    "categoria": "Categoría",
    "unidad_base": "Unidad base",
    "costo_por_unidad_base": "Costo por unidad base",
    "status": "Estado",
    "proveedor": "Proveedor",
    "notas": "Notas",
    "codigo": "Código",
    "descripcion": "Descripción",
    "orden": "Orden",
    "color": "Color",
    "es_predeterminada": "Predeterminada",
    "producto": "Producto",
    "desde_unidad": "Desde unidad",
    "hacia_unidad": "Hacia unidad",
    "factor": "Factor",
    "unidad_cobro": "Unidad de cobro",
    "decimales": "Decimales",
    "activa": "Activa",
    "orden": "Orden",
    "simbolo": "Símbolo",
    "codigo": "Código",
}


def field_label(field_name, labels=None):
    catalog = labels or FIELD_LABELS
    return catalog.get(field_name, field_name.replace("_", " ").capitalize())


def required_field_message(field_name, labels=None):
    return f"El campo «{field_label(field_name, labels)}» es obligatorio."


def invalid_number_message(field_name, labels=None):
    return f"Ingresa un número válido en «{field_label(field_name, labels)}»."


def parse_decimal(value, field_name, errors, labels=None):
    if not value:
        errors[field_name] = required_field_message(field_name, labels)
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        errors[field_name] = invalid_number_message(field_name, labels)
        return None


def form_error_context(errors):
    if not errors:
        return {}

    messages_list = list(errors.values())
    if len(messages_list) == 1:
        modal_message = messages_list[0]
    else:
        modal_message = "Revisa los siguientes campos:\n" + "\n".join(
            f"• {message}" for message in messages_list
        )

    return {
        "errors": errors,
        "error_tipo": "ER",
        "message_modal": modal_message,
    }
