from django.contrib import admin

from .models import PaymentControl


@admin.register(PaymentControl)
class PaymentControlAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "modalidad",
        "estado",
        "start_date",
        "end_date",
        "plazo_de_gracia",
        "monto",
        "moneda",
        "payment_date",
    )
    list_filter = ("estado", "modalidad", "moneda")
    search_fields = ("owner__username", "owner__email", "payment_voucher")
    raw_id_fields = ("owner", "created_by", "updated_by")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
