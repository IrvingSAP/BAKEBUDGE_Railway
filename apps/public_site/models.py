from django.db import models
from django.utils import timezone


class MensajeContacto(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "P", "Pendiente"
        LEIDO = "L", "Leído"

    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    mensaje = models.TextField()
    estado = models.CharField(
        max_length=1,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    leido_at = models.DateTimeField(null=True, blank=True)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "public_site_mensajecontacto"
        indexes = [
            models.Index(fields=["estado", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]
        ordering = ["-created_at"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self):
        return f"{self.nombre} <{self.email}> ({self.get_estado_display()})"

    @property
    def is_pendiente(self):
        return self.estado == self.Estado.PENDIENTE

    def marcar_leido(self):
        if self.estado == self.Estado.LEIDO:
            return
        self.estado = self.Estado.LEIDO
        self.leido_at = timezone.now()
        self.save(update_fields=["estado", "leido_at"])
