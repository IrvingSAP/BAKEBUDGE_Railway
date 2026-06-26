from django.contrib import admin

from apps.production.models import OrdenProduccion


@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "owner",
        "receta_version",
        "cantidad_lotes",
        "estado",
        "costo_estimado",
        "created_at",
    )
    list_filter = ("estado",)
    search_fields = ("codigo", "receta_version__receta__nombre")
    raw_id_fields = ("owner", "receta_version")
