from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .constants import STATUS_CHOICES, UNIDAD_COBRO_CHOICES, Status, UnidadCobro


class ProductCategory(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_categories",
    )
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=30, blank=True, default="")
    descripcion = models.TextField(blank=True, default="")
    orden = models.PositiveSmallIntegerField(default=0)
    color = models.CharField(max_length=7, blank=True, default="")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=Status.ACTIVO)
    es_predeterminada = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_productcategory"
        ordering = ["orden", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "nombre"],
                name="catalog_productcategory_owner_nombre_uniq",
            ),
            models.UniqueConstraint(
                fields=["owner", "codigo"],
                condition=Q(codigo__gt=""),
                name="catalog_productcategory_owner_codigo_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "status"]),
        ]

    def __str__(self):
        return self.nombre

    @property
    def is_activo(self):
        return self.status == Status.ACTIVO

    @property
    def is_usable(self):
        return self.status == Status.ACTIVO


class Producto(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="productos",
    )
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    unidad_base = models.CharField(max_length=20)
    costo_por_unidad_base = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0"),
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=Status.EN_PROCESO,
    )
    proveedor = models.CharField(max_length=120, blank=True, default="")
    notas = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_producto"
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                condition=Q(costo_por_unidad_base__gte=0),
                name="catalog_producto_costo_no_negativo",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "categoria"]),
            models.Index(fields=["owner", "nombre"]),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.categoria_id and self.owner_id and self.categoria.owner_id != self.owner_id:
            raise ValidationError({"categoria": "La categoria debe pertenecer al mismo owner del producto."})

    @property
    def is_activo(self):
        return self.status == Status.ACTIVO

    @property
    def is_en_proceso(self):
        return self.status == Status.EN_PROCESO

    @property
    def is_inactivo(self):
        return self.status == Status.INACTIVO

    @property
    def usable_en_recetas(self):
        return self.status == Status.ACTIVO


class CostoIndirecto(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="costos_indirectos",
    )
    nombre = models.CharField(max_length=50)
    unidad_cobro = models.CharField(
        max_length=15,
        choices=UNIDAD_COBRO_CHOICES,
        default=UnidadCobro.HORA,
    )
    costo_por_unidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0"),
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=Status.EN_PROCESO,
    )
    notas = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_costoindirecto"
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                condition=Q(costo_por_unidad__gte=0),
                name="catalog_costoindirecto_costo_no_negativo",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "unidad_cobro"]),
        ]

    def __str__(self):
        return self.nombre

    @property
    def is_activo(self):
        return self.status == Status.ACTIVO

    @property
    def usable_en_recetas(self):
        return self.status == Status.ACTIVO


class ConversionUnidad(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversiones_unidad",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversiones_unidad",
    )
    nombre = models.CharField(max_length=50, blank=True, default="")
    desde_unidad = models.CharField(max_length=20)
    hacia_unidad = models.CharField(max_length=20)
    factor = models.DecimalField(max_digits=12, decimal_places=6)
    notas = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_conversionunidad"
        ordering = ["desde_unidad", "hacia_unidad", "nombre"]
        constraints = [
            models.CheckConstraint(
                condition=Q(factor__gt=0),
                name="catalog_conversionunidad_factor_mayor_cero",
            ),
            models.UniqueConstraint(
                fields=["owner", "producto", "desde_unidad"],
                condition=Q(producto__isnull=False),
                name="catalog_conversionunidad_owner_producto_desde_uniq",
            ),
            models.UniqueConstraint(
                fields=["owner", "desde_unidad", "hacia_unidad"],
                condition=Q(producto__isnull=True),
                name="catalog_conversionunidad_owner_desde_hacia_generic_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "producto"]),
            models.Index(fields=["owner", "desde_unidad", "hacia_unidad"]),
        ]

    def __str__(self):
        alcance = self.producto.nombre if self.producto_id else "Generica"
        return f"{alcance}: 1 {self.desde_unidad} = {self.factor} {self.hacia_unidad}"

    def clean(self):
        if self.producto_id and self.owner_id and self.producto.owner_id != self.owner_id:
            raise ValidationError({"producto": "El producto debe pertenecer al mismo owner de la conversion."})
        if self.producto_id and self.hacia_unidad and self.hacia_unidad != self.producto.unidad_base:
            raise ValidationError({"hacia_unidad": "Debe coincidir con la unidad_base del producto."})
