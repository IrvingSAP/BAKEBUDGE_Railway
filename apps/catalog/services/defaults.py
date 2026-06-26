from decimal import Decimal

from apps.catalog.constants import Status
from apps.catalog.models import ConversionUnidad, ProductCategory


DEFAULT_CATEGORIES = (
    {"codigo": "insumo", "nombre": "Insumo", "orden": 10},
    {"codigo": "empaque", "nombre": "Empaque", "orden": 20},
    {"codigo": "decoracion", "nombre": "Decoracion", "orden": 30},
    {"codigo": "otro", "nombre": "Otro", "orden": 40},
)

DEFAULT_GENERIC_CONVERSIONS = (
    {"desde_unidad": "g", "hacia_unidad": "g", "factor": Decimal("1")},
    {"desde_unidad": "ml", "hacia_unidad": "ml", "factor": Decimal("1")},
    {"desde_unidad": "unidad", "hacia_unidad": "unidad", "factor": Decimal("1")},
    {"desde_unidad": "kg", "hacia_unidad": "g", "factor": Decimal("1000")},
    {"desde_unidad": "taza", "hacia_unidad": "g", "factor": Decimal("120")},
)


def ensure_user_catalog_defaults(user):
    if not ProductCategory.objects.filter(owner=user).exists():
        ProductCategory.objects.bulk_create(
            [
                ProductCategory(
                    owner=user,
                    codigo=item["codigo"],
                    nombre=item["nombre"],
                    orden=item["orden"],
                    es_predeterminada=True,
                    status=Status.ACTIVO,
                )
                for item in DEFAULT_CATEGORIES
            ]
        )

    if not ConversionUnidad.objects.filter(owner=user).exists():
        ConversionUnidad.objects.bulk_create(
            [
                ConversionUnidad(
                    owner=user,
                    producto=None,
                    nombre="",
                    desde_unidad=item["desde_unidad"],
                    hacia_unidad=item["hacia_unidad"],
                    factor=item["factor"],
                    notas="",
                )
                for item in DEFAULT_GENERIC_CONVERSIONS
            ]
        )
