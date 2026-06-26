"""Consultas de visibilidad de noticias."""

from datetime import date

from django.db.models import Q
from django.utils import timezone

from apps.noticias.models import Noticia


def is_visible_on_date(noticia, *, on_date: date | None = None) -> bool:
    if noticia.status != Noticia.Status.ACTIVO:
        return False
    today = on_date or timezone.localdate()
    return noticia.visible_desde <= today <= noticia.visible_hasta


def is_visible_for_user(noticia, user, *, on_date: date | None = None) -> bool:
    if not is_visible_on_date(noticia, on_date=on_date):
        return False
    if noticia.alcance == Noticia.Alcance.GLOBAL:
        return True
    return noticia.destinatarios.filter(pk=user.pk).exists()


def list_noticias_publicadas(user, *, on_date: date | None = None):
    today = on_date or timezone.localdate()
    return (
        Noticia.objects.filter(
            status=Noticia.Status.ACTIVO,
            visible_desde__lte=today,
            visible_hasta__gte=today,
        )
        .filter(
            Q(alcance=Noticia.Alcance.GLOBAL)
            | Q(alcance=Noticia.Alcance.PERSONAL, destinatarios=user)
        )
        .distinct()
        .order_by("-destacada", "-fecha_noticia", "orden")
    )


def get_noticia_visible_for_user(pk, user, *, on_date: date | None = None):
    noticia = (
        Noticia.objects.filter(pk=pk)
        .prefetch_related("destinatarios")
        .first()
    )
    if noticia is None or not is_visible_for_user(noticia, user, on_date=on_date):
        return None
    return noticia
