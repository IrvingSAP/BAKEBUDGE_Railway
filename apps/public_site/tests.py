from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.public_site.models import MensajeContacto
from apps.public_site.services.contacto_helpers import validate_contacto_form

User = get_user_model()


class ContactoFormValidationTests(TestCase):
    def test_validate_rejects_short_message(self):
        form_data = {"nombre": "Ana", "email": "ana@test.com", "mensaje": "Hola"}
        errors = {}
        validate_contacto_form(form_data, errors)
        self.assertIn("mensaje", errors)

    def test_validate_accepts_valid_data(self):
        form_data = {
            "nombre": "Ana",
            "email": "ana@test.com",
            "mensaje": "Quiero información sobre planes.",
        }
        errors = {}
        validate_contacto_form(form_data, errors)
        self.assertEqual(errors, {})


class ContactoPublicViewTests(TestCase):
    def test_post_creates_mensaje(self):
        response = self.client.post(
            reverse("public_site:contacto"),
            {
                "nombre": "María López",
                "email": "maria@example.com",
                "mensaje": "Me interesa una demo del producto.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MensajeContacto.objects.count(), 1)
        mensaje = MensajeContacto.objects.get()
        self.assertEqual(mensaje.estado, MensajeContacto.Estado.PENDIENTE)
        self.assertEqual(mensaje.nombre, "María López")

    def test_post_invalid_shows_error(self):
        response = self.client.post(
            reverse("public_site:contacto"),
            {"nombre": "", "email": "bad", "mensaje": "corto"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MensajeContacto.objects.count(), 0)


class MensajeContactoMasterTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        profile = self.master.profile
        profile.user_type = UserProfile.UserType.MASTER
        profile.email_confirmed = True
        profile.tfa_verified = True
        profile.totp_secret = "TEST"
        profile.save()

        self.user = User.objects.create_user(
            username="standard",
            email="user@example.com",
            password="testpass123",
        )
        user_profile = self.user.profile
        user_profile.user_type = UserProfile.UserType.USER
        user_profile.email_confirmed = True
        user_profile.tfa_verified = True
        user_profile.totp_secret = "TEST"
        user_profile.save()
        self._create_active_payment(self.user)

        self.mensaje = MensajeContacto.objects.create(
            nombre="Cliente",
            email="cliente@example.com",
            mensaje="Solicito acceso a la plataforma para mi negocio.",
        )

    def _create_active_payment(self, user):
        from datetime import timedelta

        from django.utils import timezone

        from apps.billing.models import PaymentControl
        from apps.core.models import Moneda

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

    def test_master_can_list(self):
        self.client.force_login(self.master)
        response = self.client.get(reverse("administration:mensajecontacto_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente")

    def test_user_cannot_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("administration:mensajecontacto_list"))
        self.assertEqual(response.status_code, 302)

    def test_master_marcar_leido(self):
        self.client.force_login(self.master)
        response = self.client.post(
            reverse("administration:mensajecontacto_detail", args=[self.mensaje.pk]),
            {"marcar_leido": "1"},
        )
        self.assertEqual(response.status_code, 302)
        self.mensaje.refresh_from_db()
        self.assertEqual(self.mensaje.estado, MensajeContacto.Estado.LEIDO)
        self.assertIsNotNone(self.mensaje.leido_at)

    def test_master_delete(self):
        self.client.force_login(self.master)
        response = self.client.post(
            reverse("administration:mensajecontacto_delete", args=[self.mensaje.pk]),
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MensajeContacto.objects.filter(pk=self.mensaje.pk).exists())
