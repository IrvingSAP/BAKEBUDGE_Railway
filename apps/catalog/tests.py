from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.catalog.models import ConversionUnidad, ProductCategory
from apps.catalog.services.defaults import (
    DEFAULT_CATEGORIES,
    DEFAULT_GENERIC_CONVERSIONS,
    ensure_user_catalog_defaults,
)

User = get_user_model()


class UserCatalogDefaultsTests(TestCase):
    def test_new_user_gets_full_conversion_seed_via_signal(self):
        user = User.objects.create_user(username="seed_test", password="test-pass-123")

        self.assertEqual(
            ProductCategory.objects.filter(owner=user).count(),
            len(DEFAULT_CATEGORIES),
        )
        self.assertEqual(
            ConversionUnidad.objects.filter(owner=user, producto__isnull=True).count(),
            len(DEFAULT_GENERIC_CONVERSIONS),
        )

    def test_existing_conversions_are_not_replaced(self):
        user = User.objects.create_user(username="seed_existing", password="test-pass-123")
        ConversionUnidad.objects.filter(owner=user).delete()
        ConversionUnidad.objects.create(
            owner=user,
            desde_unidad="oz",
            hacia_unidad="g",
            factor=Decimal("28.349523125"),
        )

        ensure_user_catalog_defaults(user)

        self.assertEqual(ConversionUnidad.objects.filter(owner=user).count(), 1)
        conv = ConversionUnidad.objects.get(owner=user)
        self.assertEqual(conv.desde_unidad, "oz")

    def test_seed_includes_key_conversions(self):
        user = User.objects.create_user(username="seed_keys", password="test-pass-123")

        pairs = set(
            ConversionUnidad.objects.filter(owner=user).values_list(
                "desde_unidad", "hacia_unidad"
            )
        )
        self.assertIn(("tz", "g"), pairs)
        self.assertIn(("taza", "ml"), pairs)
        self.assertIn(("und", "dc"), pairs)
        self.assertIn(("kg", "g"), pairs)
