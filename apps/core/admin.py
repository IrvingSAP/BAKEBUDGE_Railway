from django.contrib import admin

from .models import Moneda


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "simbolo", "decimales", "activa", "orden")
    list_filter = ("activa",)
    search_fields = ("codigo", "nombre")
    ordering = ("orden", "codigo")
