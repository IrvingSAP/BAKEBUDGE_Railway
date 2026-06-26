from django.http import Http404
from django.shortcuts import render

from apps.noticias.services.queries import get_noticia_visible_for_user, list_noticias_publicadas
from apps.security.decorators import app_access_required


@app_access_required
def noticia_feed(request):
    noticias = list_noticias_publicadas(request.user)
    return render(
        request,
        "noticias/feed.html",
        {"noticias": noticias},
    )


@app_access_required
def noticia_detail(request, pk):
    noticia = get_noticia_visible_for_user(pk, request.user)
    if noticia is None or not noticia.tiene_detalle:
        raise Http404("Noticia no encontrada.")
    return render(
        request,
        "noticias/detail.html",
        {"noticia": noticia},
    )
