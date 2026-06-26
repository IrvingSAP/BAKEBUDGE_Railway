from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.recipes.constants import STATUS_CHOICES, Status


class Receta(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recetas",
    )
    nombre = models.CharField(max_length=100)
    descripcion_corta = models.CharField(max_length=255, blank=True, default="")
    imagen = models.ImageField(upload_to="recetas/", blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=Status.EN_PROCESO,
    )
    version_actual = models.ForeignKey(
        "RecetaVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    notas = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recipes_receta"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "nombre"]),
        ]

    def __str__(self):
        return self.nombre

    @property
    def is_activa(self):
        return self.status == Status.ACTIVO

    @property
    def is_en_proceso(self):
        return self.status == Status.EN_PROCESO

    @property
    def is_inactiva(self):
        return self.status == Status.INACTIVO

    @property
    def tiene_version_actual(self):
        return self.version_actual_id is not None


class RecetaVersion(models.Model):
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="versiones",
    )
    numero_version = models.PositiveIntegerField()
    notas_cambio = models.TextField(blank=True, default="")
    rendimiento_cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("1"),
    )
    rendimiento_unidad = models.CharField(max_length=30, default="porciones")
    costo_ingredientes = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    costo_indirectos = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    costo_total = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    costo_por_porcion = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    precio_venta_sugerido = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    margen_aplicado_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("40.00"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recipes_recetaversion"
        ordering = ["receta_id", "-numero_version"]
        constraints = [
            models.UniqueConstraint(
                fields=["receta", "numero_version"],
                name="recipes_recetaversion_receta_numero_uniq",
            ),
            models.CheckConstraint(
                condition=models.Q(rendimiento_cantidad__gt=0),
                name="recipes_recetaversion_rendimiento_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.receta.nombre} v{self.numero_version}"

    @property
    def es_version_actual(self):
        return self.receta.version_actual_id == self.pk

    @property
    def etiqueta(self):
        return f"v{self.numero_version}"


class RecetaIngrediente(models.Model):
    version = models.ForeignKey(
        RecetaVersion,
        on_delete=models.CASCADE,
        related_name="ingredientes",
    )
    producto = models.ForeignKey(
        "catalog.Producto",
        on_delete=models.PROTECT,
        related_name="lineas_receta",
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    unidad = models.CharField(max_length=20)
    orden = models.PositiveIntegerField(default=0)
    notas = models.CharField(max_length=100, blank=True, default="")
    cantidad_normalizada = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        null=True,
        blank=True,
    )
    costo_linea = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )

    class Meta:
        db_table = "recipes_recetaingrediente"
        ordering = ["orden", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["version", "producto"],
                name="recipes_recetaingrediente_version_producto_uniq",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="recipes_recetaingrediente_cantidad_positiva",
            ),
        ]

    def clean(self):
        if self.producto_id and self.version_id:
            owner_id = self.version.receta.owner_id
            if self.producto.owner_id != owner_id:
                raise ValidationError(
                    {"producto": "El producto debe pertenecer al mismo owner de la receta."}
                )


class RecetaPaso(models.Model):
    version = models.ForeignKey(
        RecetaVersion,
        on_delete=models.CASCADE,
        related_name="pasos",
    )
    orden = models.PositiveIntegerField()
    instruccion = models.TextField()
    tiempo_minutos = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "recipes_recetapaso"
        ordering = ["orden", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["version", "orden"],
                name="recipes_recetapaso_version_orden_uniq",
            ),
        ]

    def clean(self):
        if self.instruccion is not None and not self.instruccion.strip():
            raise ValidationError({"instruccion": "La instrucción no puede estar vacía."})
        if self.tiempo_minutos is not None and self.tiempo_minutos <= 0:
            raise ValidationError({"tiempo_minutos": "El tiempo debe ser mayor que 0."})


class RecetaCostoIndirecto(models.Model):
    version = models.ForeignKey(
        RecetaVersion,
        on_delete=models.CASCADE,
        related_name="costos_indirectos",
    )
    costo_indirecto = models.ForeignKey(
        "catalog.CostoIndirecto",
        on_delete=models.PROTECT,
        related_name="lineas_receta",
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    costo_linea = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    orden = models.PositiveIntegerField(default=0)
    notas = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "recipes_recetacostoindirecto"
        ordering = ["orden", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["version", "costo_indirecto"],
                name="recipes_recetacostoindirecto_version_gasto_uniq",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=0),
                name="recipes_recetacostoindirecto_cantidad_no_negativa",
            ),
        ]

    def clean(self):
        if self.costo_indirecto_id and self.version_id:
            owner_id = self.version.receta.owner_id
            if self.costo_indirecto.owner_id != owner_id:
                raise ValidationError(
                    {
                        "costo_indirecto": (
                            "El costo indirecto debe pertenecer al mismo owner de la receta."
                        )
                    }
                )
