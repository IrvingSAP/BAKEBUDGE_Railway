from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.analytics.models import ProduccionAnalytics
from apps.analytics.services.record_production import record_production_analytics
from apps.analytics.services.summary import get_estadisticas_summary
from apps.billing.models import PaymentControl
from apps.catalog.constants import Status as CatalogStatus
from apps.catalog.models import CostoIndirecto, ProductCategory, Producto
from apps.catalog.services.defaults import ensure_user_catalog_defaults
from apps.core.models import Moneda
from apps.production.services.order_helpers import crear_orden
from apps.production.services.state_transitions import completar_orden, iniciar_produccion
from apps.recipes.services.receta_helpers import crear_receta_con_version_inicial
from apps.recipes.services.version_helpers import guardar_formulacion

User = get_user_model()


class AnalyticsTestBase(TestCase):
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

        categoria = ProductCategory.objects.filter(owner=self.user).first()
        self.producto = Producto.objects.create(
            owner=self.user,
            nombre="Harina",
            categoria=categoria,
            unidad_base="g",
            costo_por_unidad_base=Decimal("0.0045"),
            status=CatalogStatus.ACTIVO,
        )
        self.indirecto = CostoIndirecto.objects.create(
            owner=self.user,
            nombre="Gas",
            unidad_cobro="hora",
            costo_por_unidad=Decimal("3.50"),
            status=CatalogStatus.ACTIVO,
        )
        self.receta = crear_receta_con_version_inicial(
            self.user,
            {"nombre": "Torta", "descripcion_corta": "", "notas": "", "rendimiento_unidad": "porciones"},
            Decimal("8"),
        )
        self.version = self.receta.version_actual
        data = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "10",
            "precio_override_manual": False,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["g"],
            "ingredientes_notas": [""],
            "indirectos_gasto": [str(self.indirecto.pk)],
            "indirectos_cantidad": ["1"],
            "indirectos_notas": [""],
            "pasos_instruccion": ["Mezclar"],
            "pasos_tiempo": [""],
        }
        errors = {}
        guardar_formulacion(self.version, self.user, data, errors)
        self.assertFalse(errors)
        self.version.refresh_from_db()
        self.client.force_login(self.user)

    def _completar_orden(self):
        orden = crear_orden(self.user, self.receta, self.version, Decimal("1"))
        errors = {}
        self.assertTrue(iniciar_produccion(orden, errors))
        orden.refresh_from_db()
        self.assertTrue(
            completar_orden(
                orden,
                {"precio_venta_unitario": str(self.version.precio_venta_sugerido)},
                errors,
            )
        )
        orden.refresh_from_db()
        return orden


class ProduccionAnalyticsTests(AnalyticsTestBase):
    def test_snapshot_al_completar_orden(self):
        orden = self._completar_orden()
        self.assertTrue(ProduccionAnalytics.objects.filter(owner=self.user, orden_produccion=orden).exists())
        analytics = orden.analytics
        self.assertEqual(analytics.receta_nombre, "Torta")
        self.assertEqual(analytics.unidades_producidas, Decimal("8"))
        self.assertTrue(analytics.lineas_producto.exists())

    def test_record_idempotente(self):
        orden = self._completar_orden()
        first_id = orden.analytics.pk
        record_production_analytics(orden)
        self.assertEqual(ProduccionAnalytics.objects.filter(orden_produccion=orden).count(), 1)
        self.assertEqual(orden.analytics.pk, first_id)


class EstadisticasViewTests(AnalyticsTestBase):
    def test_estadisticas_home_vacia(self):
        response = self.client.get("/app/estadisticas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aún no hay producciones completadas")

    def test_estadisticas_home_con_datos(self):
        orden = self._completar_orden()
        response = self.client.get("/app/estadisticas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, orden.codigo)
        self.assertContains(response, "Torta")

    def test_estadisticas_aislada_por_owner(self):
        orden = self._completar_orden()
        other = User.objects.create_user(username="other", email="o@e.com", password="x")
        other.profile.email_confirmed = True
        other.profile.tfa_verified = True
        other.profile.totp_secret = "X"
        other.profile.status = UserProfile.Status.ACTIVO
        other.profile.save()
        today = timezone.localdate()
        moneda = Moneda.objects.get(codigo="COP")
        PaymentControl.objects.create(
            owner=other,
            estado=PaymentControl.Estado.ACTIVO,
            modalidad=PaymentControl.Modalidad.MENSUAL,
            moneda=moneda,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
        )
        self.client.force_login(other)
        response = self.client.get("/app/estadisticas/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, orden.codigo)

    def test_summary_kpis(self):
        self._completar_orden()
        summary = get_estadisticas_summary(self.user, {})
        self.assertEqual(summary["kpis"]["ordenes_count"], 1)
        self.assertEqual(summary["ranking_recetas"][0]["label"], "Torta")
