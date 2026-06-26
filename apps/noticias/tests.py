from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.noticias.models import Noticia
from apps.noticias.services.queries import (
    get_noticia_visible_for_user,
    is_visible_for_user,
    list_noticias_publicadas,
)

User = get_user_model()


class NoticiaVisibilityTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self.master.profile.save(update_fields=["user_type"])

        self.user_a = User.objects.create_user(
            username="usera",
            email="usera@example.com",
            password="testpass123",
        )
        self.user_a.profile.user_type = UserProfile.UserType.USER
        self.user_a.profile.save(update_fields=["user_type"])

        self.user_b = User.objects.create_user(
            username="userb",
            email="userb@example.com",
            password="testpass123",
        )
        self.user_b.profile.user_type = UserProfile.UserType.USER
        self.user_b.profile.save(update_fields=["user_type"])

        today = timezone.localdate()

        self.global_news = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Global activa",
            detalle="Contenido global",
            resumen="Resumen global",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )

        self.personal_news = Noticia.objects.create(
            alcance=Noticia.Alcance.PERSONAL,
            tipo="Aviso",
            titulo="Personal user A",
            detalle="Solo user A",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )
        self.personal_news.destinatarios.add(self.user_a)

        self.inactive_news = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Inactiva",
            detalle="No visible",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.INACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )

        self.expired_news = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Fuera de rango",
            detalle="Vencida",
            fecha_noticia=today - timedelta(days=60),
            visible_desde=today - timedelta(days=60),
            visible_hasta=today - timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )

    def test_global_visible_for_any_user(self):
        self.assertTrue(is_visible_for_user(self.global_news, self.user_a))
        self.assertTrue(is_visible_for_user(self.global_news, self.user_b))

    def test_personal_only_for_destinatario(self):
        self.assertTrue(is_visible_for_user(self.personal_news, self.user_a))
        self.assertFalse(is_visible_for_user(self.personal_news, self.user_b))

    def test_inactive_not_visible(self):
        self.assertFalse(is_visible_for_user(self.inactive_news, self.user_a))

    def test_out_of_range_not_visible(self):
        self.assertFalse(is_visible_for_user(self.expired_news, self.user_a))

    def test_list_noticias_publicadas(self):
        visible = list(list_noticias_publicadas(self.user_a))
        titles = {n.titulo for n in visible}
        self.assertIn("Global activa", titles)
        self.assertIn("Personal user A", titles)
        self.assertNotIn("Inactiva", titles)
        self.assertNotIn("Fuera de rango", titles)

    def test_list_for_user_b_excludes_personal_a(self):
        visible = list(list_noticias_publicadas(self.user_b))
        titles = {n.titulo for n in visible}
        self.assertIn("Global activa", titles)
        self.assertNotIn("Personal user A", titles)


class NoticiaDetailViewTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(
            username="master",
            email="master@example.com",
            password="testpass123",
        )
        self.master.profile.user_type = UserProfile.UserType.MASTER
        self._enable_app_access(self.master.profile)

        self.user_a = User.objects.create_user(
            username="usera",
            email="usera@example.com",
            password="testpass123",
        )
        profile_a = self.user_a.profile
        profile_a.user_type = UserProfile.UserType.USER
        self._enable_app_access(profile_a)
        self._create_active_payment(self.user_a)

        today = timezone.localdate()
        self.noticia = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Detalle test",
            detalle="Texto completo de la noticia.",
            resumen="Extracto corto",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )

        self.personal = Noticia.objects.create(
            alcance=Noticia.Alcance.PERSONAL,
            tipo="Aviso",
            titulo="Solo master",
            detalle="Privada",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )
        self.personal.destinatarios.add(self.master)

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

    def test_detail_shows_full_detalle(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f"/app/noticias/{self.noticia.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Texto completo de la noticia.")

    def test_detail_404_when_not_visible(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f"/app/noticias/{self.personal.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_get_noticia_visible_for_user(self):
        self.assertIsNotNone(get_noticia_visible_for_user(self.noticia.pk, self.user_a))
        self.assertIsNone(get_noticia_visible_for_user(self.personal.pk, self.user_a))

    def test_feed_links_to_detail(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/app/noticias/")
        self.assertContains(response, f'/app/noticias/{self.noticia.pk}/')
        self.assertContains(response, "Leer más")

    def test_feed_without_detalle_hides_leer_mas(self):
        today = timezone.localdate()
        sin_detalle = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Solo resumen",
            detalle="",
            resumen="Texto breve en tarjeta",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )
        self.client.force_login(self.user_a)
        response = self.client.get("/app/noticias/")
        self.assertContains(response, "Solo resumen")
        self.assertNotContains(response, f'/app/noticias/{sin_detalle.pk}/')

    def test_feed_without_detalle_shows_external_link(self):
        today = timezone.localdate()
        con_enlace = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Con enlace externo",
            detalle="",
            resumen="Ir al sitio del proveedor",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            enlace_externo="https://example.com/docs",
            created_by=self.master,
            updated_by=self.master,
        )
        self.client.force_login(self.user_a)
        response = self.client.get("/app/noticias/")
        self.assertContains(response, "Abrir enlace")
        self.assertContains(response, "https://example.com/docs")
        self.assertNotContains(response, f'/app/noticias/{con_enlace.pk}/')

    def test_detail_404_without_detalle(self):
        today = timezone.localdate()
        sin_detalle = Noticia.objects.create(
            alcance=Noticia.Alcance.GLOBAL,
            tipo="Aviso",
            titulo="Sin cuerpo",
            detalle="",
            resumen="Resumen",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            created_by=self.master,
            updated_by=self.master,
        )
        self.client.force_login(self.user_a)
        response = self.client.get(f"/app/noticias/{sin_detalle.pk}/")
        self.assertEqual(response.status_code, 404)


class NoticiaCopyViewTests(TestCase):
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

        self.user_a = User.objects.create_user(
            username="usera",
            email="usera@example.com",
            password="testpass123",
        )
        self.user_b = User.objects.create_user(
            username="userb",
            email="userb@example.com",
            password="testpass123",
        )

        today = timezone.localdate()
        self.noticia = Noticia.objects.create(
            alcance=Noticia.Alcance.PERSONAL,
            tipo="Aviso",
            titulo="Plantilla personal",
            detalle="Contenido de bienvenida",
            resumen="Resumen corto",
            fecha_noticia=today,
            visible_desde=today - timedelta(days=1),
            visible_hasta=today + timedelta(days=30),
            status=Noticia.Status.ACTIVO,
            destacada=True,
            orden=3,
            created_by=self.master,
            updated_by=self.master,
        )
        self.noticia.destinatarios.add(self.user_a)

    def test_master_copy_redirects_to_edit_with_clone(self):
        self.client.force_login(self.master)
        response = self.client.get(
            f"/app/administracion/noticias/{self.noticia.pk}/copiar/"
        )
        self.assertEqual(response.status_code, 302)

        clone = Noticia.objects.exclude(pk=self.noticia.pk).get()
        self.assertEqual(response.url, f"/app/administracion/noticias/{clone.pk}/editar/")
        self.assertEqual(clone.titulo, "Plantilla personal (copia)")
        self.assertEqual(clone.detalle, "Contenido de bienvenida")
        self.assertEqual(clone.alcance, Noticia.Alcance.PERSONAL)
        self.assertEqual(list(clone.destinatarios.all()), [self.user_a])
        self.assertEqual(clone.created_by, self.master)

    def test_user_cannot_copy(self):
        self.client.force_login(self.user_a)
        response = self.client.get(
            f"/app/administracion/noticias/{self.noticia.pk}/copiar/"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Noticia.objects.count(), 1)
