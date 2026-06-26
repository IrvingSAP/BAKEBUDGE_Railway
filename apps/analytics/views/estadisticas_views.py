from django.shortcuts import render

from apps.analytics.decorators import analytics_access
from apps.analytics.services.summary import get_estadisticas_summary


@analytics_access
def estadisticas_home(request):
    filtros = {
        "periodo": request.GET.get("periodo", "").strip(),
        "receta": request.GET.get("receta", "").strip(),
        "categoria": request.GET.get("categoria", "").strip(),
    }
    summary = get_estadisticas_summary(request.user, filtros)
    margen_objetivo = request.user.profile.margen_objetivo_pct
    context = {
        "summary": summary,
        "margen_objetivo": margen_objetivo,
    }
    return render(request, "analytics/estadisticas_home.html", context)
