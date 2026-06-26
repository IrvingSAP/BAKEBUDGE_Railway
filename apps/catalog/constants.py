from django.db import models


class Status(models.TextChoices):
    EN_PROCESO = "P", "En proceso"
    ACTIVO = "A", "Activo"
    INACTIVO = "I", "Inactivo"


STATUS_CHOICES = Status.choices


class UnidadCobro(models.TextChoices):
    HORA = "hora", "Hora"
    MINUTO = "minuto", "Minuto"
    LOTE = "lote", "Lote"
    PORCION = "porcion", "Porcion"
    MES = "mes", "Mes"
    FIJO = "fijo", "Fijo"


UNIDAD_COBRO_CHOICES = UnidadCobro.choices
