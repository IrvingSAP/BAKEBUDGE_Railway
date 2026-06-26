from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.production.constants import Estado


class OrdenProduccion(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ordenes_produccion",
    )
    receta_version = models.ForeignKey(
        "recipes.RecetaVersion",
        on_delete=models.PROTECT,
        related_name="ordenes_produccion",
    )
    codigo = models.CharField(max_length=20, blank=True, default="")
    cantidad_lotes = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("1"))
    fecha_programada = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True, default="")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    costo_estimado = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0"))
    precio_venta_unitario = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
    )
    precio_venta_total = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "production_ordenproduccion"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "estado"]),
            models.Index(fields=["owner", "fecha_programada"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "codigo"],
                name="production_orden_codigo_owner_uniq",
                condition=~models.Q(codigo=""),
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad_lotes__gt=0),
                name="production_orden_lotes_positivos",
            ),
        ]

    def __str__(self):
        return self.codigo or f"Orden #{self.pk}"

    @property
    def receta(self):
        return self.receta_version.receta

    @property
    def rendimiento_esperado_cantidad(self):
        return self.cantidad_lotes * self.receta_version.rendimiento_cantidad

    @property
    def rendimiento_esperado_unidad(self):
        return self.receta_version.rendimiento_unidad

    @property
    def costo_por_porcion_orden(self):
        rendimiento = self.rendimiento_esperado_cantidad
        if rendimiento <= 0:
            return Decimal("0")
        return (self.costo_estimado / rendimiento).quantize(Decimal("0.0001"))

    @property
    def es_editable(self):
        return self.estado == Estado.BORRADOR

    @property
    def fecha_listado(self):
        return self.fecha_programada or timezone.localdate(self.created_at)

    def clean(self):
        if self.receta_version_id and self.owner_id:
            if self.receta_version.receta.owner_id != self.owner_id:
                raise ValidationError(
                    {"receta_version": "La versión debe pertenecer al mismo owner de la orden."}
                )
