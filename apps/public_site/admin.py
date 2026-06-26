from django.contrib import admin

from .models import MensajeContacto


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "email", "estado", "created_at", "ip_origen")
    list_filter = ("estado",)
    search_fields = ("nombre", "email", "mensaje")
    readonly_fields = ("created_at", "leido_at")
    ordering = ("-created_at",)
