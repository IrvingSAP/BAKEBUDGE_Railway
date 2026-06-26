from django.db import models


class Estado(models.TextChoices):
    BORRADOR = "borrador", "Borrador"
    EN_PROCESO = "en_proceso", "En proceso"
    COMPLETADA = "completada", "Completada"
    CANCELADA = "cancelada", "Cancelada"


ESTADO_BADGES = {
    Estado.BORRADOR: "badge-draft",
    Estado.EN_PROCESO: "badge-active",
    Estado.COMPLETADA: "badge-active",
    Estado.CANCELADA: "badge-inactive",
}
