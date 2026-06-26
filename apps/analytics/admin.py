from django.contrib import admin

from apps.analytics.models import ProduccionAnalytics, ProduccionAnalyticsProducto


class ProduccionAnalyticsProductoInline(admin.TabularInline):
    model = ProduccionAnalyticsProducto
    extra = 0
    readonly_fields = (
        "producto",
        "producto_nombre",
        "producto_categoria",
        "cantidad_normalizada_total",
        "unidad_base",
        "costo_unitario_snapshot",
        "costo_linea_total",
    )


@admin.register(ProduccionAnalytics)
class ProduccionAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "receta_nombre",
        "receta_version_numero",
        "fecha_produccion",
        "unidades_producidas",
        "costo_produccion_total",
        "precio_venta_total",
        "ganancia_real",
    )
    list_filter = ("periodo_anio", "periodo_mes", "owner")
    readonly_fields = [f.name for f in ProduccionAnalytics._meta.fields]
    inlines = [ProduccionAnalyticsProductoInline]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
