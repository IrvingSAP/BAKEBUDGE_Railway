from django.shortcuts import get_object_or_404, render

from apps.production.decorators import production_access
from apps.production.models import OrdenProduccion


@production_access
def orden_create_help(request):
    return render(request, "production/orden_create_help.html")


@production_access
def orden_edit_help(request, pk):
    orden = get_object_or_404(OrdenProduccion, pk=pk, owner=request.user)
    return render(request, "production/orden_edit_help.html", {"orden": orden})
