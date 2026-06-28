from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.core.models import Moneda
from apps.security.services import post_login_routing, security_session, session_idle

User = get_user_model()


class PostLoginRoutingTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self._enable_security(self.master.profile)

        self.user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        profile.primer_acceso_app_completado = False
        self._enable_security(profile)
        self._create_active_payment(self.user)

    def _enable_security(self, profile):
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
                "primer_acceso_app_completado",
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

    def test_first_access_redirects_to_noticias(self):
        url = post_login_routing.resolve_post_security_redirect(self.user.profile)
        self.assertEqual(url, reverse("noticias:feed"))

    def test_subsequent_access_redirects_to_dashboard(self):
        profile = self.user.profile
        profile.primer_acceso_app_completado = True
        profile.save(update_fields=["primer_acceso_app_completado"])
        url = post_login_routing.resolve_post_security_redirect(profile)
        self.assertEqual(url, reverse("dashboard:home"))

    def test_mark_primer_acceso_only_once(self):
        profile = self.user.profile
        self.assertTrue(post_login_routing.mark_primer_acceso_completado(profile))
        profile.refresh_from_db()
        self.assertTrue(profile.primer_acceso_app_completado)
        self.assertFalse(post_login_routing.mark_primer_acceso_completado(profile))


class FirstAccessTotpFlowTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self.master.profile.email_confirmed = True
        self.master.profile.tfa_verified = True
        self.master.profile.totp_secret = "TESTSECRET"
        self.master.profile.save()

        self.user = User.objects.create_user(
            username="firsttimer",
            email="first@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        profile.email_confirmed = True
        profile.tfa_verified = True
        profile.totp_secret = "TESTSECRET"
        profile.primer_acceso_app_completado = False
        profile.save()

        today = timezone.localdate()
        from apps.billing.models import PaymentControl

        moneda = Moneda.objects.get(codigo="COP")
        PaymentControl.objects.create(
            owner=self.user,
            estado=PaymentControl.Estado.ACTIVO,
            modalidad=PaymentControl.Modalidad.MENSUAL,
            moneda=moneda,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            created_by=self.master,
            updated_by=self.master,
        )

    @patch("apps.security.views.totp_utils.verify_totp", return_value=True)
    def test_finalize_access_first_time_goes_to_noticias(self, _mock_verify):
        session = self.client.session
        session[security_session.SESSION_PENDING_USER_KEY] = self.user.pk
        session.save()

        response = self.client.post("/seguridad/totp/", {"action": "verify", "totp": "123456"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/app/noticias/")

        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.primer_acceso_app_completado)

    @patch("apps.security.views.totp_utils.verify_totp", return_value=True)
    def test_finalize_access_returning_user_goes_to_dashboard(self, _mock_verify):
        profile = self.user.profile
        profile.primer_acceso_app_completado = True
        profile.save(update_fields=["primer_acceso_app_completado"])

        session = self.client.session
        session[security_session.SESSION_PENDING_USER_KEY] = self.user.pk
        session.save()

        response = self.client.post("/seguridad/totp/", {"action": "verify", "totp": "123456"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/app/")


class AppIdleTimeoutTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self.master.profile.email_confirmed = True
        self.master.profile.tfa_verified = True
        self.master.profile.totp_secret = "TESTSECRET"
        self.master.profile.save()

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
        profile.primer_acceso_app_completado = True
        profile.save()

        today = timezone.localdate()
        from apps.billing.models import PaymentControl

        moneda = Moneda.objects.get(codigo="COP")
        PaymentControl.objects.create(
            owner=self.user,
            estado=PaymentControl.Estado.ACTIVO,
            modalidad=PaymentControl.Modalidad.MENSUAL,
            moneda=moneda,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            created_by=self.master,
            updated_by=self.master,
        )
        self.client.force_login(self.user)

    def _seed_session_activity(self, minutes_ago=0):
        session = self.client.session
        session[session_idle.SESSION_LAST_ACTIVITY_KEY] = (
            timezone.now() - timedelta(minutes=minutes_ago)
        ).isoformat()
        session.save()

    def test_app_request_refreshes_activity(self):
        self._seed_session_activity(minutes_ago=5)
        before = session_idle.get_last_activity(self.client.session)
        response = self.client.get("/app/")
        self.assertEqual(response.status_code, 200)
        after = session_idle.parse_last_activity(
            self.client.session.get(session_idle.SESSION_LAST_ACTIVITY_KEY)
        )
        self.assertIsNotNone(after)
        self.assertGreaterEqual(after, before)

    def test_app_without_activity_timestamp_logs_out(self):
        response = self.client.get("/app/perfil/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ingresar/", response.url)
        self.assertIn("idle=1", response.url)

    def test_login_gate_requires_relogin_when_idle(self):
        self._seed_session_activity(minutes_ago=41)
        response = self.client.get(reverse("security:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingresar")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_gate_auto_redirect_when_recent_activity(self):
        self._seed_session_activity(minutes_ago=10)
        response = self.client.get(reverse("security:login"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/app/"))

    def test_idle_session_logs_out_and_redirects(self):
        self._seed_session_activity(minutes_ago=41)

        response = self.client.get("/app/perfil/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ingresar/", response.url)
        self.assertIn("idle=1", response.url)

        follow = self.client.get(response.url, follow=True)
        self.assertContains(follow, "Sesión cerrada por inactividad.")

    def test_recent_activity_keeps_session(self):
        self._seed_session_activity(minutes_ago=20)

        response = self.client.get("/app/ayuda/")
        self.assertEqual(response.status_code, 200)

    def test_idle_not_enforced_outside_app(self):
        session = self.client.session
        session[session_idle.SESSION_LAST_ACTIVITY_KEY] = (
            timezone.now() - timedelta(hours=3)
        ).isoformat()
        session.save()

        response = self.client.get(reverse("public_site:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
