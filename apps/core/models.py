from django.db import models


class Moneda(models.Model):
    codigo = models.CharField(max_length=3, primary_key=True)
    nombre = models.CharField(max_length=80)
    simbolo = models.CharField(max_length=10)
    decimales = models.PositiveSmallIntegerField(default=2)
    activa = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "core_moneda"
        ordering = ["orden", "codigo"]
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"
