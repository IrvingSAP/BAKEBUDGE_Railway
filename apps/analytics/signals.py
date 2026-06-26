from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.analytics.services.record_production import record_production_analytics


@receiver(post_save, sender="production.OrdenProduccion")
def on_orden_produccion_saved(sender, instance, **kwargs):
    if instance.estado == "completada":
        record_production_analytics(instance)
