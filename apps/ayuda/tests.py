from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.billing.models import PaymentControl
from apps.catalog.services.defaults import ensure_user_catalog_defaults
from apps.core.models import Moneda

User = get_user_model()


class AyudaHomeTests(TestCase):
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

    def test_ayuda_home_ok(self):
        response = self.client.get(reverse("ayuda:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ayuda General")
        self.assertContains(response, "Panorama del ciclo")
        self.assertContains(response, reverse("accounts:perfil"))
        self.assertContains(response, reverse("catalog:producto_list"))
        self.assertContains(response, reverse("noticias:feed"))

    def test_ayuda_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("ayuda:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ingresar/", response.url)

    def test_sidebar_includes_ayuda_link(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertContains(response, reverse("ayuda:home"))
        self.assertContains(response, "Ayuda General")
