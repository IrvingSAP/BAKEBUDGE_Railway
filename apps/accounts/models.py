from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    class UserType(models.TextChoices):
        MASTER = "M", "Master"
        USER = "U", "User"

    class Status(models.TextChoices):
        ACTIVO = "A", "Activo"
        INACTIVO = "I", "Inactivo"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    nombre_negocio = models.CharField(max_length=150, blank=True, default="")
    moneda = models.ForeignKey(
        "core.Moneda",
        on_delete=models.PROTECT,
        default="COP",
        related_name="perfiles",
    )
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)
    unidad_peso_default = models.CharField(max_length=10, default="g")
    unidad_volumen_default = models.CharField(max_length=10, default="ml")
    unidad_conteo_default = models.CharField(max_length=10, default="unidad")
    margen_objetivo_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("40.00"),
    )

    user_type = models.CharField(
        max_length=1,
        choices=UserType.choices,
        default=UserType.USER,
    )

    email_confirmed = models.BooleanField(default=False)
    email_confirm_code = models.CharField(max_length=6, blank=True, null=True)
    email_confirm_exp = models.DateTimeField(blank=True, null=True)
    totp_secret = models.CharField(max_length=64, blank=True, null=True)
    tfa_verified = models.BooleanField(default=False)
    last_totp_reset = models.DateTimeField(blank=True, null=True)

    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.ACTIVO,
    )
    locked_until = models.DateTimeField(blank=True, null=True)

    primer_acceso_app_completado = models.BooleanField(
        default=False,
        help_text="True tras el primer ingreso a /app/ tras completar seguridad.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_userprofile"
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

    @property
    def is_security_complete(self):
        return (
            self.email_confirmed
            and self.tfa_verified
            and bool(self.totp_secret)
        )

    @property
    def is_active_account(self):
        if self.status != self.Status.ACTIVO:
            return False
        if self.locked_until and self.locked_until > timezone.now():
            return False
        return True

    @property
    def is_master(self):
        return self.user_type == self.UserType.MASTER

    @property
    def is_user(self):
        return self.user_type == self.UserType.USER

    @property
    def has_active_subscription(self):
        if self.is_master:
            return True
        from apps.billing.services.subscription import user_has_active_subscription

        return user_has_active_subscription(self.user)

    @property
    def can_access_app(self):
        return (
            self.is_security_complete
            and self.is_active_account
            and self.has_active_subscription
        )
