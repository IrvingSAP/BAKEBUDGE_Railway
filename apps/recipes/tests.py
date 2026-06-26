from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.core.models import Moneda
from apps.billing.models import PaymentControl
from apps.catalog.constants import Status as CatalogStatus
from apps.catalog.models import CostoIndirecto, ProductCategory, Producto
from apps.catalog.services.defaults import ensure_user_catalog_defaults
from apps.recipes.constants import Status
from apps.recipes.models import Receta, RecetaVersion
from apps.recipes.services.cost_calculator import calcular_precio_venta_sugerido
from apps.recipes.services.receta_helpers import crear_receta_con_version_inicial
from apps.recipes.services.version_helpers import crear_nueva_version, guardar_formulacion

User = get_user_model()


class RecipesTestBase(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self._enable_app_access(self.master.profile)

        self.user = User.objects.create_user(
            username="baker",
            email="baker@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        profile.margen_objetivo_pct = Decimal("40.00")
        self._enable_app_access(profile)
        self._create_active_payment(self.user)
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
        self.indirecto = CostoIndirecto.objects.filter(owner=self.user).first()
        if self.indirecto is None:
            self.indirecto = CostoIndirecto.objects.create(
                owner=self.user,
                nombre="Gas",
                unidad_cobro="hora",
                costo_por_unidad=Decimal("3.50"),
                status=CatalogStatus.ACTIVO,
            )

    def _enable_app_access(self, profile):
        profile.email_confirmed = True
        profile.tfa_verified = True
        profile.totp_secret = "TESTSECRET"
        profile.status = UserProfile.Status.ACTIVO
        profile.save(
            update_fields=[
                "email_confirmed",
                "tfa_verified",
                "totp_secret",
                "status",
                "user_type",
                "margen_objetivo_pct",
            ]
        )

    def _create_active_payment(self, user):
        today = timezone.localdate()
        moneda = Moneda.objects.get(codigo="COP")
        PaymentControl.objects.create(
            owner=user,
            estado=PaymentControl.Estado.ACTIVO,
            modalidad=PaymentControl.Modalidad.MENSUAL,
            moneda=moneda,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            created_by=self.master,
            updated_by=self.master,
        )


class CostCalculatorTests(RecipesTestBase):
    def test_precio_sugerido_con_margen(self):
        precio = calcular_precio_venta_sugerido(Decimal("10"), Decimal("40"))
        self.assertEqual(precio, Decimal("14.0000"))


class RecetaServiceTests(RecipesTestBase):
    def test_crear_receta_crea_version_v1(self):
        receta = crear_receta_con_version_inicial(
            self.user,
            {
                "nombre": "Brownie",
                "descripcion_corta": "",
                "notas": "",
                "rendimiento_unidad": "porciones",
                "marcar_activo": False,
            },
            Decimal("12"),
        )
        self.assertEqual(receta.nombre, "Brownie")
        self.assertEqual(receta.status, Status.EN_PROCESO)
        self.assertIsNotNone(receta.version_actual)
        self.assertEqual(receta.version_actual.numero_version, 1)
        self.assertEqual(receta.version_actual.rendimiento_cantidad, Decimal("12"))


class RecetaViewsTests(RecipesTestBase):
    def test_list_requires_login(self):
        response = self.client.get("/app/recetas/")
        self.assertEqual(response.status_code, 302)

    def test_create_receta_via_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/app/recetas/nuevo/",
            {
                "nombre": "Cupcake",
                "descripcion_corta": "Vainilla",
                "notas": "",
                "rendimiento_cantidad": "24",
                "rendimiento_unidad": "unidades",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Receta.objects.filter(owner=self.user, nombre="Cupcake").count(), 1)

    def test_receta_isolated_by_owner(self):
        receta = crear_receta_con_version_inicial(
            self.user,
            {"nombre": "Privada", "descripcion_corta": "", "notas": "", "rendimiento_unidad": "porciones"},
            Decimal("1"),
        )
        other = User.objects.create_user(username="other", email="o@e.com", password="testpass123")
        self._enable_app_access(other.profile)
        self._create_active_payment(other)
        self.client.force_login(other)
        response = self.client.get(f"/app/recetas/{receta.pk}/editar/")
        self.assertEqual(response.status_code, 404)


class FormulacionTests(RecipesTestBase):
    def setUp(self):
        super().setUp()
        self.receta = crear_receta_con_version_inicial(
            self.user,
            {"nombre": "Torta", "descripcion_corta": "", "notas": "", "rendimiento_unidad": "porciones"},
            Decimal("8"),
        )
        self.version = self.receta.version_actual

    def test_guardar_ingrediente_recalcula_costos(self):
        data = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "1",
            "precio_override_manual": False,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["g"],
            "ingredientes_notas": [""],
            "indirectos_gasto": [],
            "indirectos_cantidad": [],
            "indirectos_notas": [],
            "pasos_instruccion": [],
            "pasos_tiempo": [],
        }
        errors = {}
        self.assertTrue(guardar_formulacion(self.version, self.user, data, errors))
        self.version.refresh_from_db()
        self.assertEqual(self.version.ingredientes.count(), 1)
        self.assertGreater(self.version.costo_ingredientes, Decimal("0"))

    def test_unidad_invalida_rechazada(self):
        data = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "1",
            "precio_override_manual": False,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["cdta"],
            "ingredientes_notas": [""],
            "indirectos_gasto": [],
            "indirectos_cantidad": [],
            "indirectos_notas": [],
            "pasos_instruccion": [],
            "pasos_tiempo": [],
        }
        errors = {}
        self.assertFalse(guardar_formulacion(self.version, self.user, data, errors))
        self.assertTrue(any("unidad" in key for key in errors))

    def test_producto_duplicado_rechazado(self):
        base = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "1",
            "precio_override_manual": False,
            "indirectos_gasto": [],
            "indirectos_cantidad": [],
            "indirectos_notas": [],
            "pasos_instruccion": [],
            "pasos_tiempo": [],
        }
        ok_data = {
            **base,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["g"],
            "ingredientes_notas": [""],
        }
        errors = {}
        self.assertTrue(guardar_formulacion(self.version, self.user, ok_data, errors))
        self.assertEqual(self.version.ingredientes.count(), 1)

        dup_data = {
            **base,
            "ingredientes_producto": [str(self.producto.pk), str(self.producto.pk)],
            "ingredientes_cantidad": ["250", "100"],
            "ingredientes_unidad": ["g", "g"],
            "ingredientes_notas": ["", ""],
        }
        errors = {}
        self.assertFalse(guardar_formulacion(self.version, self.user, dup_data, errors))
        self.assertTrue(any("producto" in key for key in errors))
        self.version.refresh_from_db()
        self.assertEqual(self.version.ingredientes.count(), 1)
        self.assertEqual(self.version.ingredientes.first().cantidad, Decimal("250"))

    def test_guardar_indirecto_persiste_cantidad(self):
        base = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "1",
            "precio_override_manual": False,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["g"],
            "ingredientes_notas": [""],
            "pasos_instruccion": [],
            "pasos_tiempo": [],
        }
        data = {
            **base,
            "indirectos_gasto": [str(self.indirecto.pk)],
            "indirectos_cantidad": ["3.5"],
            "indirectos_notas": ["Gas"],
        }
        errors = {}
        self.assertTrue(guardar_formulacion(self.version, self.user, data, errors))
        linea = self.version.costos_indirectos.get()
        self.assertEqual(linea.cantidad, Decimal("3.5"))
        self.assertGreater(linea.costo_linea, Decimal("0"))

    def test_indirecto_cantidad_vacia_rechazada(self):
        data = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "1",
            "precio_override_manual": False,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["g"],
            "ingredientes_notas": [""],
            "indirectos_gasto": [str(self.indirecto.pk)],
            "indirectos_cantidad": [""],
            "indirectos_notas": ["Gas"],
            "pasos_instruccion": [],
            "pasos_tiempo": [],
        }
        errors = {}
        self.assertFalse(guardar_formulacion(self.version, self.user, data, errors))
        self.assertTrue(any("cantidad" in key for key in errors))
        self.assertEqual(self.version.costos_indirectos.count(), 0)

    def test_formulacion_post_indirectos_via_client(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f"/app/recetas/{self.receta.pk}/version/",
            {
                "rendimiento_cantidad": "8",
                "rendimiento_unidad": "porciones",
                "precio_venta_sugerido": "1",
                "precio_override_manual": "0",
                "ingrediente_producto": [str(self.producto.pk)],
                "ingrediente_cantidad": ["250"],
                "ingrediente_unidad": ["g"],
                "ingrediente_notas": [""],
                "indirecto_gasto": [str(self.indirecto.pk)],
                "indirecto_cantidad": ["4"],
                "indirecto_notas": ["Gas"],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.version.refresh_from_db()
        linea = self.version.costos_indirectos.get()
        self.assertEqual(linea.cantidad, Decimal("4"))

    def test_formulacion_post_indirecto_vacio_muestra_error_y_repuebla(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f"/app/recetas/{self.receta.pk}/version/",
            {
                "rendimiento_cantidad": "8",
                "rendimiento_unidad": "porciones",
                "precio_venta_sugerido": "1",
                "precio_override_manual": "0",
                "ingrediente_producto": [str(self.producto.pk)],
                "ingrediente_cantidad": ["250"],
                "ingrediente_unidad": ["g"],
                "ingrediente_notas": [""],
                "indirecto_gasto": [str(self.indirecto.pk)],
                "indirecto_cantidad": [""],
                "indirecto_notas": ["Gas"],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("indirecto_0_cantidad", response.context["errors"])
        self.assertContains(response, "Gas")
        self.assertEqual(self.version.costos_indirectos.count(), 0)

    def test_nueva_version_incrementa_numero(self):
        nueva = crear_nueva_version(self.receta, notas_cambio="Ajuste precio")
        self.assertEqual(nueva.numero_version, 2)
        self.receta.refresh_from_db()
        self.assertEqual(self.receta.version_actual.numero_version, 2)


class RecetaCostosTests(RecipesTestBase):
    def setUp(self):
        super().setUp()
        self.receta = crear_receta_con_version_inicial(
            self.user,
            {"nombre": "Torta", "descripcion_corta": "", "notas": "", "rendimiento_unidad": "porciones"},
            Decimal("8"),
        )
        self.client.force_login(self.user)

    def test_receta_costos_muestra_detalle_ingredientes(self):
        from apps.recipes.services.version_helpers import guardar_formulacion

        version = self.receta.version_actual
        data = {
            "rendimiento_cantidad": "8",
            "rendimiento_unidad": "porciones",
            "precio_venta_sugerido": "1",
            "precio_override_manual": False,
            "ingredientes_producto": [str(self.producto.pk)],
            "ingredientes_cantidad": ["250"],
            "ingredientes_unidad": ["g"],
            "ingredientes_notas": [""],
            "indirectos_gasto": [],
            "indirectos_cantidad": [],
            "indirectos_notas": [],
            "pasos_instruccion": [],
            "pasos_tiempo": [],
        }
        errors = {}
        self.assertTrue(guardar_formulacion(version, self.user, data, errors))

        response = self.client.get(f"/app/recetas/{self.receta.pk}/costos/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detalle de costos — ingredientes")
        self.assertContains(response, "Harina")
        self.assertContains(response, "Unidad base")
        self.assertContains(response, "Costo receta")

    def test_receta_costos_sin_version_redirige(self):
        receta = crear_receta_con_version_inicial(
            self.user,
            {"nombre": "Sin version", "descripcion_corta": "", "notas": "", "rendimiento_unidad": "u"},
            Decimal("1"),
        )
        version = receta.version_actual
        receta.version_actual = None
        receta.save(update_fields=["version_actual"])
        version.delete()

        response = self.client.get(f"/app/recetas/{receta.pk}/costos/")
        self.assertEqual(response.status_code, 302)
