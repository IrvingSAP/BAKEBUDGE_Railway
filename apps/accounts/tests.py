from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.accounts.services.perfil_helpers import (
    form_defaults_from_profile,
    parse_perfil_post,
    validate_perfil_form,
)
from apps.core.models import Moneda

User = get_user_model()


class PerfilValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="baker",
            email="baker@example.com",
            password="testpass123",
        )
        self.profile = self.user.profile

    def test_validate_requires_nombre_negocio(self):
        form_data = form_defaults_from_profile(self.profile)
        form_data["nombre_negocio"] = ""
        errors = {}
        validate_perfil_form(form_data, errors, profile=self.profile)
        self.assertIn("nombre_negocio", errors)

    def test_validate_rejects_negative_margen(self):
        form_data = form_defaults_from_profile(self.profile)
        form_data["margen_objetivo_pct"] = "-1"
        errors = {}
        validate_perfil_form(form_data, errors, profile=self.profile)
        self.assertIn("margen_objetivo_pct", errors)

    def test_validate_accepts_valid_form(self):
        form_data = {
            "nombre_negocio": "Dulces Demo",
            "moneda": "COP",
            "margen_objetivo_pct": "35.50",
            "unidad_peso_default": "kg",
            "unidad_volumen_default": "L",
            "unidad_conteo_default": "unidad",
        }
        errors = {}
        validate_perfil_form(form_data, errors, profile=self.profile)
        self.assertEqual(errors, {})
        self.assertEqual(form_data["margen_objetivo_pct"], Decimal("35.50"))


class PerfilViewTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self._enable_app_access(self.master.profile)

        self.user = User.objects.create_user(
            username="usera",
            email="usera@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        profile.nombre_negocio = "Antes"
        profile.margen_objetivo_pct = Decimal("40.00")
        self._enable_app_access(profile)
        self._create_active_payment(self.user)

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
                "nombre_negocio",
                "margen_objetivo_pct",
            ]
        )

    def _create_active_payment(self, user):
        from apps.billing.models import PaymentControl

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

    def test_anonymous_redirects_to_login(self):
        response = self.client.get("/app/perfil/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ingresar/", response.url)

    def test_master_can_view_perfil(self):
        self.client.force_login(self.master)
        response = self.client.get("/app/perfil/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Datos del negocio")
        self.assertContains(response, "Cuenta y seguridad")

    def test_user_can_post_valid_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/app/perfil/",
            {
                "nombre_negocio": "Repostería Nueva",
                "moneda": "COP",
                "margen_objetivo_pct": "55.25",
                "unidad_peso_default": "kg",
                "unidad_volumen_default": "L",
                "unidad_conteo_default": "unidad",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/app/perfil/")

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nombre_negocio, "Repostería Nueva")
        self.assertEqual(self.user.profile.margen_objetivo_pct, Decimal("55.25"))
        self.assertEqual(self.user.profile.unidad_peso_default, "kg")
        self.assertEqual(self.user.profile.unidad_volumen_default, "L")

    def test_post_invalid_does_not_persist(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/app/perfil/",
            {
                "nombre_negocio": "",
                "moneda": "COP",
                "margen_objetivo_pct": "40",
                "unidad_peso_default": "g",
                "unidad_volumen_default": "ml",
                "unidad_conteo_default": "unidad",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.nombre_negocio, "Antes")

    def test_incomplete_security_redirects(self):
        incomplete = User.objects.create_user(
            username="newbie",
            email="newbie@example.com",
            password="testpass123",
        )
        self.client.force_login(incomplete)
        response = self.client.get("/app/perfil/")
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(response.url, "/app/perfil/")


class ParsePerfilPostTests(TestCase):
    def test_parse_strips_fields(self):
        class FakeRequest:
            POST = {
                "nombre_negocio": "  Mi Pan  ",
                "moneda": "usd",
                "margen_objetivo_pct": " 40 ",
                "unidad_peso_default": "g",
                "unidad_volumen_default": "ml",
                "unidad_conteo_default": "unidad",
            }

        parsed = parse_perfil_post(FakeRequest())
        self.assertEqual(parsed["nombre_negocio"], "Mi Pan")
        self.assertEqual(parsed["moneda"], "USD")


class CuentaSeguridadValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="baker",
            email="baker@example.com",
            password="testpass123",
        )
        self.profile = self.user.profile
        self.profile.email_confirmed = True
        self.profile.tfa_verified = True
        self.profile.totp_secret = "TESTSECRET"
        self.profile.save()

    def test_rejects_new_password_equal_to_old(self):
        from django.test import RequestFactory

        from apps.accounts.services.cuenta_seguridad_helpers import (
            validate_cuenta_seguridad_form,
        )

        request = RequestFactory().post("/")
        form_data = {
            "password_current": "testpass123",
            "password_new": "testpass123",
            "password_confirm": "testpass123",
            "confirm_ack": True,
        }
        errors = {}
        validate_cuenta_seguridad_form(form_data, errors, request=request, user=self.user)
        self.assertIn("password_new", errors)

    def test_rejects_new_password_equal_to_username(self):
        from django.test import RequestFactory

        from apps.accounts.services.cuenta_seguridad_helpers import (
            validate_cuenta_seguridad_form,
        )

        request = RequestFactory().post("/")
        form_data = {
            "password_current": "testpass123",
            "password_new": "baker",
            "password_confirm": "baker",
            "confirm_ack": True,
        }
        errors = {}
        validate_cuenta_seguridad_form(form_data, errors, request=request, user=self.user)
        self.assertIn("password_new", errors)


class CuentaSeguridadViewTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self._enable_app_access(self.master.profile)

        self.user = User.objects.create_user(
            username="usera",
            email="usera@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        self._enable_app_access(profile)
        self._create_active_payment(self.user)

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
            ]
        )

    def _create_active_payment(self, user):
        from apps.billing.models import PaymentControl

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

    def _post_payload(self, **overrides):
        payload = {
            "password_current": "testpass123",
            "password_new": "Newpass456!",
            "password_confirm": "Newpass456!",
            "confirm_ack": "1",
        }
        payload.update(overrides)
        return payload

    def test_get_requires_login(self):
        response = self.client.get("/app/seguridad/cuenta/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ingresar/", response.url)

    def test_wrong_current_password_does_not_reset(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/app/seguridad/cuenta/",
            self._post_payload(password_current="wrongpass"),
        )
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.email_confirmed)
        self.assertEqual(self.user.profile.totp_secret, "TESTSECRET")

    def test_success_resets_security_logs_out_and_new_password_works(self):
        self.client.force_login(self.user)
        response = self.client.post("/app/seguridad/cuenta/", self._post_payload())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ingresar/", response.url)

        self.user.profile.refresh_from_db()
        self.assertFalse(self.user.profile.email_confirmed)
        self.assertFalse(self.user.profile.tfa_verified)
        self.assertIsNone(self.user.profile.totp_secret)
        self.assertIsNotNone(self.user.profile.last_totp_reset)

        self.assertFalse("_auth_user_id" in self.client.session)

        login_response = self.client.post(
            "/ingresar/",
            {"username": "usera", "password": "Newpass456!"},
        )
        self.assertEqual(login_response.status_code, 302)
        self.assertIn("/seguridad/correo/", login_response.url)

    def test_perfil_links_to_cuenta_seguridad(self):
        self.client.force_login(self.master)
        response = self.client.get("/app/perfil/")
        self.assertContains(response, 'href="/app/seguridad/cuenta/"')
