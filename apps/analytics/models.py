from decimal import Decimal

from django.conf import settings
from django.db import models


class ProduccionAnalytics(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="produccion_analytics",
    )
    orden_produccion = models.OneToOneField(
        "production.OrdenProduccion",
        on_delete=models.PROTECT,
        related_name="analytics",
    )
    receta = models.ForeignKey(
        "recipes.Receta",
        on_delete=models.PROTECT,
        related_name="produccion_analytics",
    )
    receta_version = models.ForeignKey(
        "recipes.RecetaVersion",
        on_delete=models.PROTECT,
        related_name="produccion_analytics",
    )

    receta_nombre = models.CharField(max_length=100)
    receta_version_numero = models.PositiveIntegerField()
    rendimiento_cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    rendimiento_unidad = models.CharField(max_length=30)

    costo_ingredientes = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    costo_indirectos = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    costo_version_total = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    costo_version_por_porcion = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    cantidad_lotes = models.DecimalField(max_digits=12, decimal_places=4)
    unidades_producidas = models.DecimalField(max_digits=14, decimal_places=4)
    costo_produccion_total = models.DecimalField(max_digits=14, decimal_places=4)
    costo_produccion_unitario = models.DecimalField(max_digits=14, decimal_places=4)

    margen_objetivo_pct = models.DecimalField(max_digits=5, decimal_places=2)
    precio_venta_sugerido_unitario = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    precio_venta_unitario = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    precio_venta_total = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    ganancia_estimada = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    ganancia_real = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    margen_real_pct = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    diferencia_costo = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    perdida = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    moneda_codigo = models.CharField(max_length=3)
    orden_codigo = models.CharField(max_length=20, blank=True, default="")
    periodo_anio = models.PositiveSmallIntegerField()
    periodo_mes = models.PositiveSmallIntegerField()
    fecha_produccion = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_produccionanalytics"
        ordering = ["-fecha_produccion"]
        indexes = [
            models.Index(fields=["owner", "periodo_anio", "periodo_mes"]),
            models.Index(fields=["owner", "receta"]),
            models.Index(fields=["owner", "receta_version"]),
        ]

    def __str__(self):
        return f"{self.receta_nombre} v{self.receta_version_numero} ({self.fecha_produccion:%Y-%m-%d})"


class ProduccionAnalyticsProducto(models.Model):
    analytics = models.ForeignKey(
        ProduccionAnalytics,
        on_delete=models.CASCADE,
        related_name="lineas_producto",
    )
    producto = models.ForeignKey(
        "catalog.Producto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_uso",
    )
    producto_nombre = models.CharField(max_length=150)
    producto_categoria = models.CharField(max_length=50)
    cantidad_normalizada_total = models.DecimalField(max_digits=14, decimal_places=6)
    unidad_base = models.CharField(max_length=10)
    costo_unitario_snapshot = models.DecimalField(max_digits=12, decimal_places=4)
    costo_linea_total = models.DecimalField(max_digits=14, decimal_places=4)

    class Meta:
        db_table = "analytics_produccionanalyticsproducto"
        indexes = [
            models.Index(fields=["analytics", "producto"]),
        ]

    def __str__(self):
        return f"{self.producto_nombre} ({self.cantidad_normalizada_total} {self.unidad_base})"
