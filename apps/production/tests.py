from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.billing.models import PaymentControl
from apps.catalog.constants import Status as CatalogStatus
from apps.catalog.models import CostoIndirecto, ProductCategory, Producto
from apps.catalog.services.defaults import ensure_user_catalog_defaults
from apps.core.models import Moneda
from apps.production.constants import Estado
from apps.production.models import OrdenProduccion
from apps.production.services.order_helpers import crear_orden
from apps.production.services.state_transitions import completar_orden, iniciar_produccion
from apps.recipes.services.receta_helpers import crear_receta_con_version_inicial
from apps.recipes.services.version_helpers import guardar_formulacion

User = get_user_model()


class ProductionTestBase(TestCase):
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


class OrdenProduccionTests(ProductionTestBase):
    def test_crear_orden_calcula_costo(self):
        orden = crear_orden(self.user, self.receta, self.version, Decimal("2"))
        self.assertTrue(orden.codigo.startswith("OP-"))
        self.assertEqual(orden.estado, Estado.BORRADOR)
        self.assertEqual(orden.costo_estimado, self.version.costo_total * Decimal("2"))

    def test_crear_orden_via_client(self):
        response = self.client.post(
            "/app/produccion/nueva/",
            {
                "receta_id": str(self.receta.pk),
                "cantidad_lotes": "1",
                "fecha_programada": "",
                "notas": "Pedido cliente",
            },
        )
        self.assertEqual(response.status_code, 302)
        orden = OrdenProduccion.objects.get(owner=self.user)
        self.assertEqual(orden.notas, "Pedido cliente")

    def test_iniciar_y_completar_orden(self):
        orden = crear_orden(self.user, self.receta, self.version, Decimal("1"))
        errors = {}
        self.assertTrue(iniciar_produccion(orden, errors))
        orden.refresh_from_db()
        self.assertEqual(orden.estado, Estado.EN_PROCESO)
        costo_congelado = orden.costo_estimado

        self.assertTrue(
            completar_orden(
                orden,
                {"precio_venta_unitario": str(self.version.precio_venta_sugerido)},
                errors,
            )
        )
        orden.refresh_from_db()
        self.assertEqual(orden.estado, Estado.COMPLETADA)
        self.assertEqual(orden.costo_estimado, costo_congelado)
        self.assertIsNotNone(orden.precio_venta_unitario)

    def test_orden_aislada_por_owner(self):
        orden = crear_orden(self.user, self.receta, self.version, Decimal("1"))
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
        response = self.client.get(f"/app/produccion/{orden.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_listado_ordenes(self):
        crear_orden(self.user, self.receta, self.version, Decimal("1"))
        response = self.client.get("/app/produccion/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OP-")
