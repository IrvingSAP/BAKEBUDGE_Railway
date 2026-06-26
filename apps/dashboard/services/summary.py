"""Estadísticas del dashboard — datos del usuario conectado."""

from django.db.models import Avg
from django.utils import timezone

from apps.analytics.models import ProduccionAnalytics
from apps.catalog.constants import Status
from apps.catalog.models import Producto
from apps.production.constants import ESTADO_BADGES, Estado
from apps.production.models import OrdenProduccion
from apps.recipes.models import Receta

ESTADO_LABELS = dict(Estado.choices)


def get_dashboard_summary(user):
    profile = user.profile
    margen_objetivo = profile.margen_objetivo_pct
    productos_qs = Producto.objects.filter(owner=user)
    productos_activos = productos_qs.filter(status=Status.ACTIVO).count()
    productos_total = productos_qs.count()

    recetas_qs = Receta.objects.filter(owner=user)
    recetas_total = recetas_qs.count()
    recetas_vigentes = recetas_qs.filter(version_actual__isnull=False).count()

    today = timezone.localdate()
    ordenes_qs = OrdenProduccion.objects.filter(owner=user)
    ordenes_mes = ordenes_qs.filter(
        fecha_programada__year=today.year,
        fecha_programada__month=today.month,
    ).count()
    ordenes_completadas = ordenes_qs.filter(estado=Estado.COMPLETADA).count()

    analytics_qs = ProduccionAnalytics.objects.filter(owner=user)
    margen_avg = analytics_qs.aggregate(m=Avg("margen_real_pct"))["m"]
    margen_promedio = margen_avg if margen_avg is not None else margen_objetivo

    produccion_reciente = []
    for orden in (
        ordenes_qs.select_related("receta_version__receta")
        .order_by("-updated_at")[:5]
    ):
        version = orden.receta_version
        produccion_reciente.append(
            {
                "pk": orden.pk,
                "codigo": orden.codigo,
                "receta": f"{version.receta.nombre} {version.etiqueta}",
                "estado_class": ESTADO_BADGES.get(orden.estado, "badge-draft"),
                "estado_label": ESTADO_LABELS.get(orden.estado, orden.estado),
                "costo": orden.costo_estimado,
            }
        )

    return {
        "productos_activos": productos_activos,
        "recetas": recetas_total,
        "recetas_vigentes": recetas_vigentes,
        "ordenes_mes": ordenes_mes,
        "ordenes_completadas": ordenes_completadas,
        "margen_promedio": margen_promedio,
        "margen_objetivo": margen_objetivo,
        "tiene_productos": productos_total > 0,
        "tiene_recetas": recetas_total > 0,
        "produccion_reciente": produccion_reciente,
    }
