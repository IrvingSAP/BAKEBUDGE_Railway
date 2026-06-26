"""Creación y validación de cabecera Receta."""

from decimal import Decimal

from django.db import transaction

from apps.recipes.constants import Status as RecetaStatus
from apps.recipes.models import Receta, RecetaVersion
from apps.recipes.services.cost_calculator import actualizar_precio_sugerido_version


def parse_receta_create_post(post, files=None):
    return {
        "nombre": post.get("nombre", "").strip(),
        "descripcion_corta": post.get("descripcion_corta", "").strip(),
        "notas": post.get("notas", "").strip(),
        "rendimiento_cantidad": post.get("rendimiento_cantidad", "").strip(),
        "rendimiento_unidad": post.get("rendimiento_unidad", "porciones").strip(),
        "marcar_activo": post.get("marcar_activo") in {"1", "true", "on"},
        "imagen": files.get("imagen") if files else None,
    }


def parse_receta_edit_post(post, files=None):
    data = parse_receta_create_post(post, files)
    data["status"] = post.get("status", RecetaStatus.EN_PROCESO).strip()
    data.pop("rendimiento_cantidad", None)
    data.pop("rendimiento_unidad", None)
    data.pop("marcar_activo", None)
    return data


def validate_receta_create(data, errors):
    if not data["nombre"]:
        errors["nombre"] = "El nombre es obligatorio."
    elif len(data["nombre"]) > 100:
        errors["nombre"] = "El nombre no puede superar 100 caracteres."

    rendimiento = _parse_positive_decimal(
        data.get("rendimiento_cantidad"),
        "rendimiento_cantidad",
        errors,
    )
    if rendimiento is not None and rendimiento <= 0:
        errors["rendimiento_cantidad"] = "El rendimiento debe ser mayor que 0."

    unidad = data.get("rendimiento_unidad", "").strip()
    if not unidad:
        errors["rendimiento_unidad"] = "La unidad de rendimiento es obligatoria."
    elif len(unidad) > 30:
        errors["rendimiento_unidad"] = "La unidad no puede superar 30 caracteres."

    return rendimiento


def validate_receta_edit(data, errors):
    if not data["nombre"]:
        errors["nombre"] = "El nombre es obligatorio."
    status_values = {value for value, _ in RecetaStatus.choices}
    if data.get("status") not in status_values:
        errors["status"] = "Selecciona un estado válido."


def _parse_positive_decimal(raw, field_name, errors):
    if raw in (None, ""):
        errors[field_name] = "Este campo es obligatorio."
        return None
    try:
        value = Decimal(str(raw).replace(",", "."))
    except Exception:
        errors[field_name] = "Ingresa un número válido."
        return None
    return value


@transaction.atomic
def crear_receta_con_version_inicial(owner, data, rendimiento_cantidad):
    status = RecetaStatus.ACTIVO if data.get("marcar_activo") else RecetaStatus.EN_PROCESO
    receta = Receta(
        owner=owner,
        nombre=data["nombre"],
        descripcion_corta=data.get("descripcion_corta", ""),
        notas=data.get("notas", ""),
        status=status,
    )
    if data.get("imagen"):
        receta.imagen = data["imagen"]
    receta.save()

    version = RecetaVersion.objects.create(
        receta=receta,
        numero_version=1,
        rendimiento_cantidad=rendimiento_cantidad,
        rendimiento_unidad=data.get("rendimiento_unidad") or "porciones",
    )
    actualizar_precio_sugerido_version(version)
    version.save(update_fields=["precio_venta_sugerido", "margen_aplicado_pct"])

    receta.version_actual = version
    receta.save(update_fields=["version_actual"])
    return receta
