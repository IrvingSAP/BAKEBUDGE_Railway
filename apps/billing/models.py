from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class PaymentControl(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACTIVO = "activo", "Activo"
        SUSPENDIDO = "suspendido", "Suspendido"
        CONSUMIDO = "consumido", "Consumido"

    class Modalidad(models.TextChoices):
        MENSUAL = "M", "Mensual"
        ANUAL = "A", "Anual"

    class PaymentMethod(models.TextChoices):
        BANCO = "banco", "Banco"
        TRANSFERENCIA = "transferencia", "Transferencia"
        PAGOMOVIL = "pagomovil", "Pago móvil"
        EFECTIVO = "efectivo", "Efectivo"
        OTROS = "otros", "Otros"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_controls",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    plazo_de_gracia = models.PositiveSmallIntegerField(
        default=0,
        db_column="plazoDeGracia",
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        verbose_name="Plazo de gracia (días)",
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        default="",
    )
    payment_voucher = models.CharField(max_length=50, blank=True, default="")
    monto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    moneda = models.ForeignKey(
        "core.Moneda",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_controls",
    )
    modalidad = models.CharField(
        max_length=1,
        choices=Modalidad.choices,
        default=Modalidad.MENSUAL,
    )
    other_data = models.CharField(max_length=100, blank=True, default="")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_controls_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_controls_updated",
    )

    class Meta:
        db_table = "billing_paymentcontrol"
        verbose_name = "Control de pago"
        verbose_name_plural = "Controles de pago"
        ordering = ["-payment_date", "-start_date", "-created_at"]
        indexes = [
            models.Index(fields=["owner", "estado"]),
        ]

    def __str__(self):
        return f"{self.owner.username} — {self.get_estado_display()} ({self.pk})"

    @property
    def effective_end_date(self):
        from apps.billing.services.subscription import effective_end_date as _effective_end_date

        return _effective_end_date(self)

    @property
    def is_vigente(self):
        from apps.billing.services.subscription import is_payment_vigente

        return is_payment_vigente(self)

    @property
    def is_expired(self):
        from apps.billing.services.subscription import is_payment_expired

        return is_payment_expired(self)

    @property
    def monto_display(self):
        if self.monto in (None, ""):
            return ""
        moneda = self.moneda
        simbolo = getattr(moneda, "simbolo", "$")
        decimales = getattr(moneda, "decimales", 2)
        codigo = getattr(moneda, "codigo", "")
        amount = Decimal(self.monto)
        formatted = f"{simbolo} {amount:,.{decimales}f}"
        if codigo:
            return f"{formatted} {codigo}"
        return formatted
