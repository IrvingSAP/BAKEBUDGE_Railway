"""Transiciones de estado de OrdenProduccion."""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.production.constants import Estado
from apps.production.services.order_cost import calcular_costo_estimado, recalcular_costo_estimado


def _parse_precio(raw, field_key, errors, required=False):
    if raw in (None, ""):
        if required:
            errors[field_key] = "Este campo es obligatorio."
        return None
    try:
        value = Decimal(str(raw).replace(",", "."))
    except Exception:
        errors[field_key] = "Ingresa un número válido."
        return None
    if value < 0:
        errors[field_key] = "El precio no puede ser negativo."
        return None
    return value


@transaction.atomic
def iniciar_produccion(orden, errors):
    if orden.estado != Estado.BORRADOR:
        errors["estado"] = "Solo puedes iniciar órdenes en borrador."
        return False
    recalcular_costo_estimado(orden)
    orden.costo_estimado = calcular_costo_estimado(orden)
    orden.estado = Estado.EN_PROCESO
    orden.fecha_inicio = timezone.now()
    orden.save(
        update_fields=["costo_estimado", "estado", "fecha_inicio", "updated_at"]
    )
    return True


@transaction.atomic
def cancelar_orden(orden, errors):
    if orden.estado not in (Estado.BORRADOR, Estado.EN_PROCESO):
        errors["estado"] = "Esta orden ya está cerrada."
        return False
    orden.estado = Estado.CANCELADA
    orden.fecha_completada = timezone.now()
    orden.save(update_fields=["estado", "fecha_completada", "updated_at"])
    return True


@transaction.atomic
def completar_orden(orden, post, errors):
    if orden.estado != Estado.EN_PROCESO:
        errors["estado"] = "Solo puedes completar órdenes en proceso."
        return False

    precio_unitario = _parse_precio(
        post.get("precio_venta_unitario", "").strip(),
        "precio_venta_unitario",
        errors,
    )
    precio_total = _parse_precio(
        post.get("precio_venta_total", "").strip(),
        "precio_venta_total",
        errors,
    )
    if errors:
        return False

    version = orden.receta_version
    if precio_unitario is None and precio_total is None:
        precio_unitario = version.precio_venta_sugerido
    elif precio_unitario is None and precio_total is not None:
        rendimiento = orden.rendimiento_esperado_cantidad
        if rendimiento > 0:
            precio_unitario = (precio_total / rendimiento).quantize(Decimal("0.0001"))
        else:
            precio_unitario = Decimal("0")
    elif precio_total is None and precio_unitario is not None:
        precio_total = (precio_unitario * orden.rendimiento_esperado_cantidad).quantize(
            Decimal("0.0001")
        )

    orden.precio_venta_unitario = precio_unitario
    orden.precio_venta_total = precio_total
    orden.estado = Estado.COMPLETADA
    orden.fecha_completada = timezone.now()
    orden.save(
        update_fields=[
            "precio_venta_unitario",
            "precio_venta_total",
            "estado",
            "fecha_completada",
            "updated_at",
        ]
    )
    return True
