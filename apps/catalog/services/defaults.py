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
    # --- Peso (16) ---
    {"nombre": "Peso", "desde_unidad": "kg", "hacia_unidad": "kg", "factor": Decimal("1")},
    {"nombre": "Peso", "desde_unidad": "kg", "hacia_unidad": "lb", "factor": Decimal("2.2046226218")},
    {"nombre": "Peso", "desde_unidad": "kg", "hacia_unidad": "oz", "factor": Decimal("35.2739619496")},
    {"nombre": "Peso", "desde_unidad": "kg", "hacia_unidad": "g", "factor": Decimal("1000")},
    {"nombre": "Peso", "desde_unidad": "lb", "hacia_unidad": "kg", "factor": Decimal("0.45359237")},
    {"nombre": "Peso", "desde_unidad": "lb", "hacia_unidad": "g", "factor": Decimal("453.59237")},
    {"nombre": "Peso", "desde_unidad": "lb", "hacia_unidad": "oz", "factor": Decimal("16")},
    {"nombre": "Peso", "desde_unidad": "lb", "hacia_unidad": "lb", "factor": Decimal("1")},
    {"nombre": "Peso", "desde_unidad": "oz", "hacia_unidad": "kg", "factor": Decimal("0.028349523125")},
    {"nombre": "Peso", "desde_unidad": "oz", "hacia_unidad": "g", "factor": Decimal("28.349523125")},
    {"nombre": "Peso", "desde_unidad": "oz", "hacia_unidad": "lb", "factor": Decimal("0.0625")},
    {"nombre": "Peso", "desde_unidad": "oz", "hacia_unidad": "oz", "factor": Decimal("1")},
    {"nombre": "Peso", "desde_unidad": "g", "hacia_unidad": "kg", "factor": Decimal("0.001")},
    {"nombre": "Peso", "desde_unidad": "g", "hacia_unidad": "lb", "factor": Decimal("0.0022046226218")},
    {"nombre": "Peso", "desde_unidad": "g", "hacia_unidad": "oz", "factor": Decimal("0.0352739619496")},
    {"nombre": "Peso", "desde_unidad": "g", "hacia_unidad": "g", "factor": Decimal("1")},
    # --- Fluidos (9) ---
    {"nombre": "Fluidos", "desde_unidad": "gl", "hacia_unidad": "gl", "factor": Decimal("1")},
    {"nombre": "Fluidos", "desde_unidad": "gl", "hacia_unidad": "lt", "factor": Decimal("3.785411784")},
    {"nombre": "Fluidos", "desde_unidad": "gl", "hacia_unidad": "ml", "factor": Decimal("3785.411784")},
    {"nombre": "Fluidos", "desde_unidad": "lt", "hacia_unidad": "lt", "factor": Decimal("1")},
    {"nombre": "Fluidos", "desde_unidad": "lt", "hacia_unidad": "gl", "factor": Decimal("0.2641720524")},
    {"nombre": "Fluidos", "desde_unidad": "lt", "hacia_unidad": "ml", "factor": Decimal("1000")},
    {"nombre": "Fluidos", "desde_unidad": "ml", "hacia_unidad": "ml", "factor": Decimal("1")},
    {"nombre": "Fluidos", "desde_unidad": "ml", "hacia_unidad": "gl", "factor": Decimal("0.0002641720524")},
    {"nombre": "Fluidos", "desde_unidad": "ml", "hacia_unidad": "lt", "factor": Decimal("0.001")},
    # --- Taza → volumen (6) ---
    {"nombre": "Taza", "desde_unidad": "tz", "hacia_unidad": "ml", "factor": Decimal("240")},
    {"nombre": "Taza", "desde_unidad": "t3/4", "hacia_unidad": "ml", "factor": Decimal("180")},
    {"nombre": "Taza", "desde_unidad": "t2/3", "hacia_unidad": "ml", "factor": Decimal("160")},
    {"nombre": "Taza", "desde_unidad": "t1/2", "hacia_unidad": "ml", "factor": Decimal("120")},
    {"nombre": "Taza", "desde_unidad": "t1/3", "hacia_unidad": "ml", "factor": Decimal("80")},
    {"nombre": "Taza", "desde_unidad": "t1/4", "hacia_unidad": "ml", "factor": Decimal("60")},
    # --- Taza → peso, aprox. sólidos (6) ---
    {"nombre": "Taza", "desde_unidad": "tz", "hacia_unidad": "g", "factor": Decimal("120")},
    {"nombre": "Taza", "desde_unidad": "t3/4", "hacia_unidad": "g", "factor": Decimal("90")},
    {"nombre": "Taza", "desde_unidad": "t2/3", "hacia_unidad": "g", "factor": Decimal("80")},
    {"nombre": "Taza", "desde_unidad": "t1/2", "hacia_unidad": "g", "factor": Decimal("60")},
    {"nombre": "Taza", "desde_unidad": "t1/3", "hacia_unidad": "g", "factor": Decimal("40")},
    {"nombre": "Taza", "desde_unidad": "t1/4", "hacia_unidad": "g", "factor": Decimal("30")},
    # --- Alias «taza» (compat. docs) (2) ---
    {"nombre": "Taza", "desde_unidad": "taza", "hacia_unidad": "ml", "factor": Decimal("240")},
    {"nombre": "Taza", "desde_unidad": "taza", "hacia_unidad": "g", "factor": Decimal("120")},
    # --- Unidad / docena (5) ---
    {"nombre": "Unidad", "desde_unidad": "dc", "hacia_unidad": "dc", "factor": Decimal("1")},
    {"nombre": "Unidad", "desde_unidad": "dc", "hacia_unidad": "und", "factor": Decimal("12")},
    {"nombre": "Unidad", "desde_unidad": "und", "hacia_unidad": "und", "factor": Decimal("1")},
    {"nombre": "Unidad", "desde_unidad": "und", "hacia_unidad": "dc", "factor": Decimal("0.083333333333")},
    {"nombre": "Unidad", "desde_unidad": "unidad", "hacia_unidad": "unidad", "factor": Decimal("1")},
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
                    nombre=item.get("nombre", ""),
                    desde_unidad=item["desde_unidad"],
                    hacia_unidad=item["hacia_unidad"],
                    factor=item["factor"],
                    notas="",
                )
                for item in DEFAULT_GENERIC_CONVERSIONS
            ]
        )
