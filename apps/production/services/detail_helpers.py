"""Contexto de detalle: ingredientes/pasos/indirectos escalados por lotes."""

from decimal import Decimal


def _escalar(valor, lotes):
    return (Decimal(valor) * lotes).quantize(Decimal("0.0001"))


def orden_detalle_context(orden):
    version = orden.receta_version
    lotes = orden.cantidad_lotes

    ingredientes = []
    for linea in version.ingredientes.select_related("producto").order_by("orden", "id"):
        ingredientes.append(
            {
                "producto": linea.producto.nombre,
                "cantidad_base": linea.cantidad,
                "cantidad_escalada": _escalar(linea.cantidad, lotes),
                "unidad": linea.unidad,
                "costo_linea": _escalar(linea.costo_linea, lotes),
            }
        )

    indirectos = []
    for linea in version.costos_indirectos.select_related("costo_indirecto").order_by(
        "orden", "id"
    ):
        indirectos.append(
            {
                "nombre": linea.costo_indirecto.nombre,
                "cantidad_base": linea.cantidad,
                "cantidad_escalada": _escalar(linea.cantidad, lotes),
                "unidad_cobro": linea.costo_indirecto.unidad_cobro,
                "costo_linea": _escalar(linea.costo_linea, lotes),
            }
        )

    pasos = list(version.pasos.all())

    return {
        "ingredientes_escalados": ingredientes,
        "indirectos_escalados": indirectos,
        "pasos": pasos,
        "costo_ingredientes_escalado": _escalar(version.costo_ingredientes, lotes),
        "costo_indirectos_escalado": _escalar(version.costo_indirectos, lotes),
    }
