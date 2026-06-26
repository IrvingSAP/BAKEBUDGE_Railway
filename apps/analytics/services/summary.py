"""Agregaciones de lectura para la pantalla de estadísticas."""

from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import Coalesce

from apps.analytics.models import ProduccionAnalytics, ProduccionAnalyticsProducto
from apps.recipes.models import Receta

MESES_CORTOS = (
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)


def periodo_label(anio, mes):
    if not anio or not mes:
        return ""
    return f"{MESES_CORTOS[mes - 1]} {anio}"


def base_qs(user):
    return ProduccionAnalytics.objects.filter(owner=user)


def parse_periodo(periodo):
    if not periodo:
        return None, None
    try:
        anio_str, mes_str = periodo.split("-", 1)
        return int(anio_str), int(mes_str)
    except (TypeError, ValueError):
        return None, None


def apply_filters(qs, *, periodo_anio=None, periodo_mes=None, receta_id=None):
    if periodo_anio is not None and periodo_mes is not None:
        qs = qs.filter(periodo_anio=periodo_anio, periodo_mes=periodo_mes)
    if receta_id:
        qs = qs.filter(receta_id=receta_id)
    return qs


def _with_bar_pct(items, value_key, display_key=None):
    if not items:
        return []
    max_val = items[0][value_key]
    result = []
    for item in items:
        pct = round((item[value_key] / max_val) * 100) if max_val else 0
        row = dict(item)
        row["pct"] = pct
        if display_key:
            row["display"] = item[display_key]
        result.append(row)
    return result


def get_periodo_options(user):
    rows = (
        base_qs(user)
        .values("periodo_anio", "periodo_mes")
        .distinct()
        .order_by("-periodo_anio", "-periodo_mes")
    )
    return [
        {
            "value": f"{row['periodo_anio']}-{row['periodo_mes']:02d}",
            "label": periodo_label(row["periodo_anio"], row["periodo_mes"]),
        }
        for row in rows
    ]


def get_receta_options(user):
    return Receta.objects.filter(owner=user).order_by("nombre")


def get_categoria_options(user):
    return (
        ProduccionAnalyticsProducto.objects.filter(analytics__owner=user)
        .exclude(producto_categoria="")
        .values_list("producto_categoria", flat=True)
        .distinct()
        .order_by("producto_categoria")
    )


def compute_kpis(qs):
    agg = qs.aggregate(
        margen_avg=Avg("margen_real_pct"),
        ganancia_total=Coalesce(Sum("ganancia_real"), Decimal("0")),
        ordenes_count=Count("id"),
        perdidas_count=Count("id", filter=Q(perdida__isnull=False)),
    )
    return agg


def ranking_recetas(qs):
    rows = list(
        qs.values("receta_nombre")
        .annotate(lotes=Sum("cantidad_lotes"))
        .order_by("-lotes")[:5]
    )
    items = [
        {
            "label": row["receta_nombre"],
            "value": row["lotes"],
            "display": f"{row['lotes']} lotes",
        }
        for row in rows
    ]
    return _with_bar_pct(items, "value")


def ranking_insumos(analytics_qs, categoria=None):
    analytics_ids = list(analytics_qs.values_list("id", flat=True))
    if not analytics_ids:
        return []
    lineas = ProduccionAnalyticsProducto.objects.filter(analytics_id__in=analytics_ids)
    if categoria:
        lineas = lineas.filter(producto_categoria=categoria)
    rows = list(
        lineas.values("producto_nombre", "unidad_base")
        .annotate(cantidad=Sum("cantidad_normalizada_total"))
        .order_by("-cantidad")[:5]
    )
    items = [
        {
            "label": row["producto_nombre"],
            "value": row["cantidad"],
            "display": f"{row['cantidad']:.1f} {row['unidad_base']}",
            "secondary": True,
        }
        for row in rows
    ]
    return _with_bar_pct(items, "value")


def ranking_versiones(qs):
    rows = list(
        qs.values("receta_nombre", "receta_version_numero")
        .annotate(unidades=Sum("unidades_producidas"))
        .order_by("-unidades")[:5]
    )
    items = [
        {
            "label": f"{row['receta_nombre']} v{row['receta_version_numero']}",
            "value": row["unidades"],
            "display": f"{row['unidades']} u.",
        }
        for row in rows
    ]
    return _with_bar_pct(items, "value")


def evolucion_costo(qs):
    rows = list(
        qs.values("periodo_anio", "periodo_mes")
        .annotate(costo_avg=Avg("costo_produccion_unitario"))
        .order_by("periodo_anio", "periodo_mes")
    )
    if not rows:
        return []
    max_val = max(row["costo_avg"] for row in rows)
    result = []
    for row in rows:
        costo = row["costo_avg"]
        result.append(
            {
                "label": periodo_label(row["periodo_anio"], row["periodo_mes"]),
                "value": costo,
                "display": f"${costo:.2f} / u.",
                "pct": round((costo / max_val) * 100) if max_val else 0,
            }
        )
    return result


def ratio_indirectos(qs):
    rows = qs.filter(costo_ingredientes__gt=0).values_list(
        "costo_indirectos", "costo_ingredientes"
    )
    ratios = [ci / ing for ci, ing in rows if ing > 0]
    if not ratios:
        return None
    return sum(ratios) / len(ratios)


def get_estadisticas_summary(user, filtros=None):
    filtros = filtros or {}
    periodo = filtros.get("periodo", "")
    receta_id = filtros.get("receta", "")
    categoria = filtros.get("categoria", "")

    anio, mes = parse_periodo(periodo)
    receta_id_int = int(receta_id) if str(receta_id).isdigit() else None

    qs = apply_filters(
        base_qs(user),
        periodo_anio=anio,
        periodo_mes=mes,
        receta_id=receta_id_int,
    )
    ratio = ratio_indirectos(qs)

    return {
        "kpis": compute_kpis(qs),
        "ranking_recetas": ranking_recetas(qs),
        "ranking_insumos": ranking_insumos(qs, categoria or None),
        "ranking_versiones": ranking_versiones(qs),
        "evolucion_costo": evolucion_costo(qs),
        "ratio_indirectos": ratio,
        "ratio_indirectos_pct": min(100, round(ratio * 100)) if ratio is not None else 0,
        "ratio_indirectos_label": f"{ratio * 100:.1f}" if ratio is not None else None,
        "filas": qs.select_related("orden_produccion"),
        "periodo_options": get_periodo_options(user),
        "receta_options": get_receta_options(user),
        "categoria_options": get_categoria_options(user),
        "filtros": {
            "periodo": periodo,
            "receta": receta_id,
            "categoria": categoria,
        },
        "periodo_hint": periodo_label(anio, mes) if anio and mes else "Periodo filtrado",
    }
