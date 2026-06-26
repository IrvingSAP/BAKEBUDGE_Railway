from django.contrib import admin
from .models import ConversionUnidad, CostoIndirecto, ProductCategory, Producto


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "nombre",
        "codigo",
        "orden",
        "status",
        "es_predeterminada",
        "updated_at",
    )
    list_filter = ("status", "es_predeterminada")
    search_fields = ("nombre", "codigo", "owner__username")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "nombre",
        "categoria",
        "unidad_base",
        "costo_por_unidad_base",
        "status",
        "updated_at",
    )
    list_filter = ("status", "categoria")
    search_fields = ("nombre", "proveedor", "owner__username")


@admin.register(CostoIndirecto)
class CostoIndirectoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "nombre",
        "unidad_cobro",
        "costo_por_unidad",
        "status",
        "updated_at",
    )
    list_filter = ("status", "unidad_cobro")
    search_fields = ("nombre", "owner__username")


@admin.register(ConversionUnidad)
class ConversionUnidadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "producto",
        "nombre",
        "desde_unidad",
        "hacia_unidad",
        "factor",
        "updated_at",
    )
    list_filter = ("hacia_unidad", "desde_unidad")
    search_fields = ("nombre", "desde_unidad", "hacia_unidad", "owner__username")
