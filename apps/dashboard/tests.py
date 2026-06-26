from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.billing.models import PaymentControl
from apps.catalog.constants import Status as CatalogStatus
from apps.catalog.models import CostoIndirecto, ProductCategory, Producto
from apps.catalog.services.defaults import ensure_user_catalog_defaults
from apps.core.models import Moneda
from apps.production.services.order_helpers import crear_orden
from apps.recipes.services.receta_helpers import crear_receta_con_version_inicial
from apps.recipes.services.version_helpers import guardar_formulacion

User = get_user_model()


class DashboardHomeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="baker",
            email="baker@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        profile.email_confirmed = True
        profile.tfa_verified = True
        profile.totp_secret = "TESTSECRET"
        profile.status = UserProfile.Status.ACTIVO
        profile.margen_objetivo_pct = Decimal("40.00")
        profile.save()

        today = timezone.localdate()
        moneda = Moneda.objects.get(codigo="COP")
        PaymentControl.objects.create(
            owner=self.user,
            estado=PaymentControl.Estado.ACTIVO,
            modalidad=PaymentControl.Modalidad.MENSUAL,
            moneda=moneda,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
        )
        ensure_user_catalog_defaults(self.user)
        self.client.force_login(self.user)

    def test_dashboard_enlaces_modulos(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("catalog:producto_list"))
        self.assertContains(response, reverse("recipes:receta_list"))
        self.assertContains(response, reverse("production:orden_list"))
        self.assertContains(response, reverse("analytics:estadisticas_home"))

    def test_produccion_reciente_enlaza_detalle(self):
        categoria = ProductCategory.objects.filter(owner=self.user).first()
        producto = Producto.objects.create(
            owner=self.user,
            nombre="Harina",
            categoria=categoria,
            unidad_base="g",
            costo_por_unidad_base=Decimal("0.0045"),
            status=CatalogStatus.ACTIVO,
        )
        indirecto = CostoIndirecto.objects.create(
            owner=self.user,
            nombre="Gas",
            unidad_cobro="hora",
            costo_por_unidad=Decimal("3.50"),
            status=CatalogStatus.ACTIVO,
        )
        receta = crear_receta_con_version_inicial(
            self.user,
            {"nombre": "Torta", "descripcion_corta": "", "notas": "", "rendimiento_unidad": "porciones"},
            Decimal("8"),
        )
        version = receta.version_actual
        errors = {}
        guardar_formulacion(
            version,
            self.user,
            {
                "rendimiento_cantidad": "8",
                "rendimiento_unidad": "porciones",
                "precio_venta_sugerido": "10",
                "precio_override_manual": False,
                "ingredientes_producto": [str(producto.pk)],
                "ingredientes_cantidad": ["250"],
                "ingredientes_unidad": ["g"],
                "ingredientes_notas": [""],
                "indirectos_gasto": [str(indirecto.pk)],
                "indirectos_cantidad": ["1"],
                "indirectos_notas": [""],
                "pasos_instruccion": ["Mezclar"],
                "pasos_tiempo": [""],
            },
            errors,
        )
        self.assertFalse(errors)
        orden = crear_orden(self.user, receta, version, Decimal("1"))

        response = self.client.get(reverse("dashboard:home"))
        self.assertContains(response, orden.codigo)
        self.assertContains(response, reverse("production:orden_detail", kwargs={"pk": orden.pk}))
