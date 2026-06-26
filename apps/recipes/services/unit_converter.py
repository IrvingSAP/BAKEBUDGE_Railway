"""Normalización de unidades para cálculo de costos en recetas."""

from decimal import Decimal

from django.db.models import Q

from apps.catalog.models import ConversionUnidad


def _normalize_unit(value: str) -> str:
    return (value or "").strip().lower()


def buscar_conversion(owner, producto, unidad_receta):
    """Devuelve factor para convertir unidad_receta → unidad_base del producto."""
    unidad = _normalize_unit(unidad_receta)
    base = _normalize_unit(producto.unidad_base)
    if not unidad or unidad == base:
        return Decimal("1")

    conversiones = ConversionUnidad.objects.filter(owner=owner).filter(
        Q(producto=producto) | Q(producto__isnull=True)
    )

    candidatas = []
    for conv in conversiones:
        if _normalize_unit(conv.desde_unidad) != unidad:
            continue
        if _normalize_unit(conv.hacia_unidad) != base:
            continue
        candidatas.append(conv)

    if not candidatas:
        return None

    def sort_key(conv):
        return (0 if conv.producto_id else 1, conv.pk)

    candidatas.sort(key=sort_key)
    return candidatas[0].factor


def normalizar_cantidad(owner, producto, cantidad, unidad_receta):
    """
    Convierte cantidad en unidad_receta a unidad_base del producto.
    Retorna (cantidad_normalizada, aviso) donde aviso es str o None.
    """
    unidad = _normalize_unit(unidad_receta)
    base = _normalize_unit(producto.unidad_base)
    if unidad == base or not unidad:
        return cantidad, None

    factor = buscar_conversion(owner, producto, unidad_receta)
    if factor is None:
        return None, (
            f"Sin conversión {unidad_receta}→{producto.unidad_base}; "
            "configure en Conversiones."
        )
    return (cantidad * factor).quantize(Decimal("0.000001")), None
