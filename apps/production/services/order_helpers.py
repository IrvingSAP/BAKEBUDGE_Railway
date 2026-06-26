"""Alta, edición y parseo de OrdenProduccion."""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.production.constants import Estado
from apps.production.models import OrdenProduccion
from apps.production.services.order_cost import recalcular_costo_estimado
from apps.recipes.constants import Status as RecetaStatus
from apps.recipes.models import Receta


def _parse_decimal(raw, field_key, errors, min_value=None):
    if raw in (None, ""):
        errors[field_key] = "Este campo es obligatorio."
        return None
    try:
        value = Decimal(str(raw).replace(",", "."))
    except Exception:
        errors[field_key] = "Ingresa un número válido."
        return None
    if min_value is not None and value < min_value:
        errors[field_key] = f"El valor debe ser al menos {min_value}."
    return value


def generar_codigo(owner) -> str:
    year = timezone.localdate().year
    prefix = f"OP-{year}-"
    existentes = OrdenProduccion.objects.filter(owner=owner, codigo__startswith=prefix).count()
    return f"{prefix}{existentes + 1:03d}"


def get_receta_for_order(owner, receta_id):
    return Receta.objects.select_related("version_actual").filter(
        owner=owner,
        pk=receta_id,
    ).first()


def recetas_para_planificacion(owner):
    return (
        Receta.objects.filter(owner=owner)
        .select_related("version_actual")
        .exclude(version_actual__isnull=True)
        .order_by("nombre")
    )


def recetas_preview_data(owner):
    data = {}
    for receta in recetas_para_planificacion(owner):
        version = receta.version_actual
        data[str(receta.pk)] = {
            "nombre": receta.nombre,
            "status": receta.status,
            "version_etiqueta": version.etiqueta,
            "version_id": version.pk,
            "costo_total": str(version.costo_total),
            "rendimiento_cantidad": str(version.rendimiento_cantidad),
            "rendimiento_unidad": version.rendimiento_unidad,
            "precio_sugerido": str(version.precio_venta_sugerido),
        }
    return data


def parse_orden_create_post(post):
    return {
        "receta_id": post.get("receta_id", "").strip(),
        "cantidad_lotes": post.get("cantidad_lotes", "").strip(),
        "fecha_programada": post.get("fecha_programada", "").strip(),
        "notas": post.get("notas", "").strip(),
    }


def parse_orden_edit_post(post):
    return {
        "cantidad_lotes": post.get("cantidad_lotes", "").strip(),
        "fecha_programada": post.get("fecha_programada", "").strip(),
        "notas": post.get("notas", "").strip(),
    }


def validate_orden_create(owner, data, errors):
    if not data["receta_id"]:
        errors["receta_id"] = "Selecciona una receta."
        return None, None, None

    receta = get_receta_for_order(owner, data["receta_id"])
    if receta is None:
        errors["receta_id"] = "Receta no válida."
        return None, None, None

    version = receta.version_actual
    if version is None:
        errors["receta_id"] = "La receta no tiene versión vigente."
        return None, None, None

    lotes = _parse_decimal(
        data["cantidad_lotes"],
        "cantidad_lotes",
        errors,
        min_value=Decimal("0.0001"),
    )
    if errors:
        return None, None, None
    return receta, version, lotes


def validate_orden_edit(data, errors):
    lotes = _parse_decimal(
        data["cantidad_lotes"],
        "cantidad_lotes",
        errors,
        min_value=Decimal("0.0001"),
    )
    return lotes


def avisos_receta(receta, version):
    avisos = []
    if receta.status == RecetaStatus.EN_PROCESO:
        avisos.append("La receta está en proceso — completa la formulación antes de producir.")
    if version.costo_total <= 0:
        avisos.append("La versión vigente no tiene costos calculados.")
    return avisos


@transaction.atomic
def crear_orden(owner, receta, version, lotes, fecha_programada=None, notas=""):
    orden = OrdenProduccion(
        owner=owner,
        receta_version=version,
        codigo=generar_codigo(owner),
        cantidad_lotes=lotes,
        fecha_programada=fecha_programada or None,
        notas=(notas or "").strip(),
        estado=Estado.BORRADOR,
    )
    recalcular_costo_estimado(orden)
    orden.full_clean()
    orden.save()
    return orden


@transaction.atomic
def actualizar_orden_borrador(orden, lotes, fecha_programada=None, notas=""):
    if orden.estado != Estado.BORRADOR:
        raise ValueError("Solo se editan órdenes en borrador.")
    orden.cantidad_lotes = lotes
    orden.fecha_programada = fecha_programada or None
    orden.notas = (notas or "").strip()
    recalcular_costo_estimado(orden)
    orden.save(
        update_fields=[
            "cantidad_lotes",
            "fecha_programada",
            "notas",
            "costo_estimado",
            "updated_at",
        ]
    )
    return orden
