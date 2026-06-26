"""Cálculo de costos estimados para OrdenProduccion."""

from decimal import Decimal

from apps.production.constants import Estado
from apps.production.models import OrdenProduccion


def calcular_costo_estimado(orden) -> Decimal:
    version = orden.receta_version
    return (orden.cantidad_lotes * version.costo_total).quantize(Decimal("0.0001"))


def recalcular_costo_estimado(orden) -> None:
    if orden.estado != Estado.BORRADOR:
        return
    orden.costo_estimado = calcular_costo_estimado(orden)


def preview_planificacion(receta_version, cantidad_lotes) -> dict:
    lotes = Decimal(str(cantidad_lotes))
    costo_estimado = (lotes * receta_version.costo_total).quantize(Decimal("0.0001"))
    rendimiento = lotes * receta_version.rendimiento_cantidad
    costo_porcion = Decimal("0")
    if rendimiento > 0:
        costo_porcion = (costo_estimado / rendimiento).quantize(Decimal("0.0001"))
    return {
        "costo_estimado": costo_estimado,
        "rendimiento_esperado": rendimiento,
        "rendimiento_unidad": receta_version.rendimiento_unidad,
        "costo_por_porcion": costo_porcion,
        "precio_sugerido": receta_version.precio_venta_sugerido,
    }
