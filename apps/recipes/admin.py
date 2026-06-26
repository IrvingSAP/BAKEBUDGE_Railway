from django.contrib import admin

from apps.recipes.models import (
    Receta,
    RecetaCostoIndirecto,
    RecetaIngrediente,
    RecetaPaso,
    RecetaVersion,
)


class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 0


class RecetaCostoIndirectoInline(admin.TabularInline):
    model = RecetaCostoIndirecto
    extra = 0


class RecetaPasoInline(admin.TabularInline):
    model = RecetaPaso
    extra = 0


class RecetaVersionInline(admin.TabularInline):
    model = RecetaVersion
    extra = 0
    fields = ("numero_version", "rendimiento_cantidad", "rendimiento_unidad", "costo_total")
    readonly_fields = fields
    show_change_link = True


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "owner", "status", "version_actual", "updated_at")
    list_filter = ("status",)
    search_fields = ("nombre", "owner__username")
    inlines = [RecetaVersionInline]


@admin.register(RecetaVersion)
class RecetaVersionAdmin(admin.ModelAdmin):
    list_display = (
        "receta",
        "numero_version",
        "rendimiento_cantidad",
        "costo_total",
        "precio_venta_sugerido",
    )
    inlines = [RecetaIngredienteInline, RecetaCostoIndirectoInline, RecetaPasoInline]
