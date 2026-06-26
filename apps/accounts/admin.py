from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "nombre_negocio",
        "user_type",
        "status",
        "moneda",
        "email_confirmed",
        "tfa_verified",
        "created_at",
    )
    list_filter = ("user_type", "status", "email_confirmed", "tfa_verified", "moneda")
    search_fields = ("user__username", "user__email", "nombre_negocio")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)
    ordering = ("-created_at",)
