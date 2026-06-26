from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.administration.services.facturacion_helpers import (
    validate_form,
    validate_plazo_de_gracia,
)
from apps.billing.models import PaymentControl
from apps.billing.services.subscription import (
    effective_end_date,
    expire_overdue_payments,
    is_payment_expired,
    is_payment_vigente,
    user_has_active_subscription,
)
from apps.core.models import Moneda

User = get_user_model()


class PaymentControlModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="billinguser",
            email="billing@example.com",
            password="testpass123",
        )
        profile = self.user.profile
        profile.user_type = UserProfile.UserType.USER
        profile.save(update_fields=["user_type"])
        self.moneda = Moneda.objects.get(codigo="COP")

    def _create_payment(self, **kwargs):
        defaults = {
            "owner": self.user,
            "estado": PaymentControl.Estado.ACTIVO,
            "modalidad": PaymentControl.Modalidad.MENSUAL,
            "moneda": self.moneda,
        }
        defaults.update(kwargs)
        return PaymentControl.objects.create(**defaults)

    def test_effective_end_date_includes_grace(self):
        today = timezone.localdate()
        payment = self._create_payment(
            start_date=today - timedelta(days=10),
            end_date=today,
            plazo_de_gracia=5,
        )
        self.assertEqual(effective_end_date(payment), today + timedelta(days=5))

    def test_is_vigente_within_grace_period(self):
        today = timezone.localdate()
        payment = self._create_payment(
            start_date=today - timedelta(days=40),
            end_date=today - timedelta(days=2),
            plazo_de_gracia=5,
        )
        self.assertTrue(is_payment_vigente(payment))
        self.assertTrue(payment.is_vigente)

    def test_is_vigente_after_grace_period(self):
        today = timezone.localdate()
        payment = self._create_payment(
            start_date=today - timedelta(days=40),
            end_date=today - timedelta(days=10),
            plazo_de_gracia=3,
        )
        self.assertFalse(is_payment_vigente(payment))
        self.assertTrue(is_payment_expired(payment))

    def test_user_has_active_subscription_uses_grace(self):
        today = timezone.localdate()
        self._create_payment(
            start_date=today - timedelta(days=40),
            end_date=today - timedelta(days=1),
            plazo_de_gracia=7,
        )
        self.assertTrue(user_has_active_subscription(self.user))
        self.assertTrue(self.user.profile.has_active_subscription)

    def test_expire_overdue_payments_at_login(self):
        today = timezone.localdate()
        payment = self._create_payment(
            start_date=today - timedelta(days=40),
            end_date=today - timedelta(days=10),
            plazo_de_gracia=0,
        )
        updated = expire_overdue_payments(self.user)
        payment.refresh_from_db()
        self.assertEqual(updated, 1)
        self.assertEqual(payment.estado, PaymentControl.Estado.CONSUMIDO)
        self.assertFalse(user_has_active_subscription(self.user))

    def test_expire_does_not_touch_vigente_payment(self):
        today = timezone.localdate()
        payment = self._create_payment(
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=20),
            plazo_de_gracia=3,
        )
        updated = expire_overdue_payments(self.user)
        payment.refresh_from_db()
        self.assertEqual(updated, 0)
        self.assertEqual(payment.estado, PaymentControl.Estado.ACTIVO)


class FacturacionValidationTests(TestCase):
    def test_plazo_de_gracia_defaults_to_zero(self):
        form_data = {"plazo_de_gracia": ""}
        errors = {}
        validate_plazo_de_gracia(form_data, errors)
        self.assertEqual(errors, {})
        self.assertEqual(form_data["plazo_de_gracia"], 0)

    def test_plazo_de_gracia_rejects_out_of_range(self):
        form_data = {"plazo_de_gracia": "31"}
        errors = {}
        validate_plazo_de_gracia(form_data, errors)
        self.assertIn("plazo_de_gracia", errors)

    def test_validate_form_accepts_valid_plazo(self):
        form_data = {
            "modalidad": PaymentControl.Modalidad.MENSUAL,
            "estado": PaymentControl.Estado.PENDIENTE,
            "plazo_de_gracia": "15",
            "monto": "",
        }
        errors = {}
        validate_form(form_data, errors)
        self.assertEqual(errors, {})
        self.assertEqual(form_data["plazo_de_gracia"], 15)
