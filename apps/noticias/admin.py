from django.contrib import admin

from .models import Noticia


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "tipo",
        "alcance",
        "status",
        "fecha_noticia",
        "visible_desde",
        "visible_hasta",
        "destacada",
    )
    list_filter = ("status", "alcance", "destacada")
    search_fields = ("titulo", "tipo", "detalle")
    filter_horizontal = ("destinatarios",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("created_by", "updated_by")
