from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Noticia(models.Model):
    class Alcance(models.TextChoices):
        GLOBAL = "G", "Global"
        PERSONAL = "P", "Personal"

    class Status(models.TextChoices):
        ACTIVO = "A", "Activo"
        INACTIVO = "I", "Inactivo"

    alcance = models.CharField(
        max_length=1,
        choices=Alcance.choices,
        default=Alcance.GLOBAL,
    )
    destinatarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="noticias_personales",
    )
    tipo = models.CharField(max_length=20)
    titulo = models.CharField(max_length=200)
    detalle = models.TextField(blank=True, default="")
    resumen = models.CharField(max_length=300, blank=True, default="")
    fecha_noticia = models.DateField()
    visible_desde = models.DateField()
    visible_hasta = models.DateField()
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.ACTIVO,
    )
    destacada = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)
    enlace_interno = models.CharField(max_length=200, blank=True, default="")
    enlace_externo = models.URLField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="noticias_creadas",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="noticias_actualizadas",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "noticias_noticia"
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ["-destacada", "-fecha_noticia", "orden"]
        indexes = [
            models.Index(fields=["status", "visible_desde", "visible_hasta"]),
            models.Index(fields=["alcance", "fecha_noticia"]),
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        errors = {}
        if self.visible_desde and self.visible_hasta and self.visible_hasta < self.visible_desde:
            errors["visible_hasta"] = "La fecha «visible hasta» debe ser posterior o igual a «visible desde»."
        if self.alcance == self.Alcance.PERSONAL and self.pk:
            if not self.destinatarios.exists():
                errors["destinatarios"] = "Selecciona al menos un destinatario para noticias personales."
        if errors:
            raise ValidationError(errors)

    @property
    def is_visible_hoy(self):
        from apps.noticias.services.queries import is_visible_on_date

        return is_visible_on_date(self)

    def visible_para(self, user):
        from apps.noticias.services.queries import is_visible_for_user

        return is_visible_for_user(self, user)

    @property
    def tiene_detalle(self):
        return bool((self.detalle or "").strip())

    @property
    def resumen_display(self):
        from apps.noticias.services.display import resumen_texto

        return resumen_texto(self)
