"""
Cálculo de costos y precio de venta sugerido para RecetaVersion.
Ver docs/BAKEBUDGE_MODELS.md#recetaversion
"""

from decimal import Decimal

from django.db.models import Sum

from apps.recipes.services.unit_converter import normalizar_cantidad


def list_ingredientes_costo_detalle(version):
    """Filas de detalle de costo por ingrediente (solo lectura)."""
    lineas = []
    for ing in version.ingredientes.select_related("producto").order_by("orden", "id"):
        producto = ing.producto
        lineas.append(
            {
                "producto_nombre": producto.nombre,
                "cantidad": ing.cantidad,
                "unidad_base": producto.unidad_base,
                "costo_base": producto.costo_por_unidad_base,
                "unidad_receta": ing.unidad,
                "costo_receta": ing.costo_linea,
                "cantidad_normalizada": ing.cantidad_normalizada,
                "sin_conversion": ing.cantidad_normalizada is None,
            }
        )
    return lineas


def list_indirectos_costo_detalle(version):
    """Filas de detalle de costo por gasto indirecto (solo lectura)."""
    lineas = []
    for linea in version.costos_indirectos.select_related("costo_indirecto").order_by(
        "orden", "id"
    ):
        gasto = linea.costo_indirecto
        lineas.append(
            {
                "nombre": gasto.nombre,
                "cantidad": linea.cantidad,
                "unidad_cobro": gasto.unidad_cobro,
                "tarifa": gasto.costo_por_unidad,
                "costo_linea": linea.costo_linea,
            }
        )
    return lineas


def calcular_precio_venta_sugerido(
    costo_por_porcion: Decimal,
    margen_pct: Decimal,
) -> Decimal:
    """precio_venta_sugerido = costo_por_porcion × (1 + margen/100)"""
    if costo_por_porcion <= 0:
        return Decimal("0")
    factor = Decimal("1") + (margen_pct / Decimal("100"))
    return (costo_por_porcion * factor).quantize(Decimal("0.0001"))


def calcular_costo_linea_ingrediente(owner, producto, cantidad, unidad):
    """Calcula cantidad_normalizada y costo_linea; retorna dict con aviso opcional."""
    cantidad_norm, aviso = normalizar_cantidad(owner, producto, cantidad, unidad)
    if cantidad_norm is None:
        return {
            "cantidad_normalizada": None,
            "costo_linea": Decimal("0"),
            "aviso": aviso,
        }
    costo = (cantidad_norm * producto.costo_por_unidad_base).quantize(Decimal("0.0001"))
    return {
        "cantidad_normalizada": cantidad_norm,
        "costo_linea": costo,
        "aviso": aviso,
    }


def calcular_costo_linea_indirecto(costo_indirecto, cantidad):
    return (cantidad * costo_indirecto.costo_por_unidad).quantize(Decimal("0.0001"))


def recalcular_linea_ingrediente(linea):
    owner = linea.version.receta.owner
    resultado = calcular_costo_linea_ingrediente(
        owner,
        linea.producto,
        linea.cantidad,
        linea.unidad,
    )
    linea.cantidad_normalizada = resultado["cantidad_normalizada"]
    linea.costo_linea = resultado["costo_linea"]
    return resultado.get("aviso")


def recalcular_linea_indirecto(linea):
    linea.costo_linea = calcular_costo_linea_indirecto(linea.costo_indirecto, linea.cantidad)


def recalcular_totales_version(version, margen_pct=None, actualizar_precio=True):
    """Recalcula caches de costos y opcionalmente precio sugerido."""
    for linea in version.ingredientes.select_related("producto"):
        recalcular_linea_ingrediente(linea)
        linea.save(update_fields=["cantidad_normalizada", "costo_linea"])

    for linea in version.costos_indirectos.select_related("costo_indirecto"):
        recalcular_linea_indirecto(linea)
        linea.save(update_fields=["costo_linea"])

    costo_ingredientes = version.ingredientes.aggregate(
        total=Sum("costo_linea")
    )["total"] or Decimal("0")
    costo_indirectos = version.costos_indirectos.aggregate(
        total=Sum("costo_linea")
    )["total"] or Decimal("0")
    costo_total = costo_ingredientes + costo_indirectos

    if version.rendimiento_cantidad > 0:
        costo_por_porcion = (costo_total / version.rendimiento_cantidad).quantize(
            Decimal("0.0001")
        )
    else:
        costo_por_porcion = Decimal("0")

    version.costo_ingredientes = costo_ingredientes
    version.costo_indirectos = costo_indirectos
    version.costo_total = costo_total
    version.costo_por_porcion = costo_por_porcion

    if actualizar_precio:
        actualizar_precio_sugerido_version(version, margen_pct=margen_pct)

    version.save(
        update_fields=[
            "costo_ingredientes",
            "costo_indirectos",
            "costo_total",
            "costo_por_porcion",
            "precio_venta_sugerido",
            "margen_aplicado_pct",
            "updated_at",
        ]
    )


def actualizar_precio_sugerido_version(version, margen_pct=None) -> None:
    """
    Actualiza precio_venta_sugerido y margen_aplicado_pct en la versión.
    margen_pct: si None, usa owner.profile.margen_objetivo_pct.
    """
    if margen_pct is None:
        margen_pct = version.receta.owner.profile.margen_objetivo_pct
    version.margen_aplicado_pct = margen_pct
    version.precio_venta_sugerido = calcular_precio_venta_sugerido(
        version.costo_por_porcion,
        margen_pct,
    )
