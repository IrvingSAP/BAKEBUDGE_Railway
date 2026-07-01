from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.catalog.models import ConversionUnidad, ProductCategory
from apps.catalog.services.defaults import DEFAULT_GENERIC_CONVERSIONS

User = get_user_model()


class UsuarioCreateFacturacionFlowTests(TestCase):
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
        profile.totp_secret = "TESTSECRET"
        profile.status = UserProfile.Status.ACTIVO
        profile.save()

    def _create_user_payload(self, **overrides):
        payload = {
            "username": "nuevo.user",
            "email": "nuevo@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Nuevo",
            "last_name": "User",
            "is_active": "1",
            "nombre_negocio": "Repostería Demo",
            "user_type": UserProfile.UserType.USER,
            "moneda": "COP",
            "status": UserProfile.Status.ACTIVO,
        }
        payload.update(overrides)
        return payload

    def test_user_create_redirects_to_facturacion_with_owner(self):
        self.client.force_login(self.master)
        response = self.client.post(
            reverse("administration:usuario_create"),
            self._create_user_payload(),
        )

        created = User.objects.get(username="nuevo.user")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f"{reverse('administration:facturacion_create')}?owner={created.pk}",
        )

    def test_facturacion_create_preselects_owner_and_moneda(self):
        self.client.force_login(self.master)
        create_response = self.client.post(
            reverse("administration:usuario_create"),
            self._create_user_payload(username="billing.user", email="billing@example.com"),
        )
        created = User.objects.get(username="billing.user")
        self.assertEqual(create_response.status_code, 302)

        response = self.client.get(create_response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "recién creado")
        self.assertContains(response, "billing.user")
        self.assertContains(response, 'name="owner"')
        self.assertContains(response, f'value="{created.pk}"')
        self.assertContains(response, "Repostería Demo")
        self.assertContains(response, 'value="COP" selected')

    def test_user_create_seeds_catalog_defaults(self):
        self.client.force_login(self.master)
        self.client.post(
            reverse("administration:usuario_create"),
            self._create_user_payload(username="seed.user", email="seed@example.com"),
        )

        created = User.objects.get(username="seed.user")
        self.assertTrue(ProductCategory.objects.filter(owner=created).exists())
        self.assertEqual(
            ConversionUnidad.objects.filter(owner=created, producto__isnull=True).count(),
            len(DEFAULT_GENERIC_CONVERSIONS),
        )

    def test_master_create_redirects_to_usuario_list(self):
        self.client.force_login(self.master)
        response = self.client.post(
            reverse("administration:usuario_create"),
            self._create_user_payload(
                username="otro.master",
                email="otro.master@example.com",
                user_type=UserProfile.UserType.MASTER,
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("administration:usuario_list"))
