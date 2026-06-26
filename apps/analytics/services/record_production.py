"""
Crea snapshot analítico al completar una OrdenProduccion.
Ver docs/BAKEBUDGE_MODELS.md#produccionanalytics
"""

from decimal import Decimal

from django.db import transaction

from apps.analytics.models import ProduccionAnalytics, ProduccionAnalyticsProducto


def _resolve_sale_prices(orden, version, unidades):
    """Retorna (unitario, total, sugerido_unitario)."""
    sugerido_u = version.precio_venta_sugerido
    if orden.precio_venta_total is not None:
        total = orden.precio_venta_total
        unitario = total / unidades if unidades else Decimal("0")
        return unitario, total, sugerido_u
    if orden.precio_venta_unitario is not None:
        unitario = orden.precio_venta_unitario
        return unitario, unitario * unidades, sugerido_u
    unitario = sugerido_u
    return unitario, unitario * unidades, sugerido_u


def _compute_margins(
    *,
    unidades: Decimal,
    costo_total: Decimal,
    costo_unitario: Decimal,
    precio_sugerido_u: Decimal,
    precio_total: Decimal,
) -> dict:
    ganancia_estimada = (precio_sugerido_u - costo_unitario) * unidades
    ganancia_real = precio_total - costo_total
    margen_real_pct = None
    if precio_total > 0:
        margen_real_pct = (ganancia_real / precio_total) * Decimal("100")
    perdida = abs(ganancia_real) if ganancia_real < 0 else None
    return {
        "ganancia_estimada": ganancia_estimada,
        "ganancia_real": ganancia_real,
        "margen_real_pct": margen_real_pct,
        "diferencia_costo": ganancia_real,
        "perdida": perdida,
    }


@transaction.atomic
def record_production_analytics(orden):
    """
    Registra analytics para una orden completada.
    Retorna None si la orden no está completada o ya tiene snapshot.
    """
    if orden.estado != "completada":
        return None
    if hasattr(orden, "analytics"):
        return orden.analytics

    version = orden.receta_version
    receta = version.receta
    owner = orden.owner
    profile = owner.profile

    rendimiento = version.rendimiento_cantidad
    unidades = orden.cantidad_lotes * rendimiento
    costo_total = orden.costo_estimado
    costo_unitario = costo_total / unidades if unidades else Decimal("0")

    precio_u, precio_total, sugerido_u = _resolve_sale_prices(orden, version, unidades)
    margen_objetivo = profile.margen_objetivo_pct
    margins = _compute_margins(
        unidades=unidades,
        costo_total=costo_total,
        costo_unitario=costo_unitario,
        precio_sugerido_u=sugerido_u,
        precio_total=precio_total,
    )

    fecha = orden.fecha_completada
    moneda_codigo = profile.moneda_id

    analytics = ProduccionAnalytics.objects.create(
        owner=owner,
        orden_produccion=orden,
        receta=receta,
        receta_version=version,
        receta_nombre=receta.nombre,
        receta_version_numero=version.numero_version,
        rendimiento_cantidad=rendimiento,
        rendimiento_unidad=version.rendimiento_unidad,
        costo_ingredientes=version.costo_ingredientes,
        costo_indirectos=version.costo_indirectos,
        costo_version_total=version.costo_total,
        costo_version_por_porcion=version.costo_por_porcion,
        cantidad_lotes=orden.cantidad_lotes,
        unidades_producidas=unidades,
        costo_produccion_total=costo_total,
        costo_produccion_unitario=costo_unitario,
        margen_objetivo_pct=margen_objetivo,
        precio_venta_sugerido_unitario=sugerido_u,
        precio_venta_unitario=precio_u,
        precio_venta_total=precio_total,
        moneda_codigo=moneda_codigo,
        orden_codigo=orden.codigo or "",
        periodo_anio=fecha.year,
        periodo_mes=fecha.month,
        fecha_produccion=fecha,
        **margins,
    )

    lineas = []
    ingredientes = version.ingredientes.select_related("producto", "producto__categoria")
    for ingrediente in ingredientes:
        producto = ingrediente.producto
        factor = orden.cantidad_lotes
        cantidad_norm = (ingrediente.cantidad_normalizada or Decimal("0")) * factor
        costo_linea = ingrediente.costo_linea * factor
        categoria_nombre = producto.categoria.nombre if producto.categoria_id else ""
        lineas.append(
            ProduccionAnalyticsProducto(
                analytics=analytics,
                producto=producto,
                producto_nombre=producto.nombre,
                producto_categoria=categoria_nombre,
                cantidad_normalizada_total=cantidad_norm,
                unidad_base=producto.unidad_base,
                costo_unitario_snapshot=producto.costo_por_unidad_base,
                costo_linea_total=costo_linea,
            )
        )
    ProduccionAnalyticsProducto.objects.bulk_create(lineas)
    return analytics
