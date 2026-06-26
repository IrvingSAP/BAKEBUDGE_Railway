from django import template

from apps.noticias.models import Noticia
from apps.noticias.services.display import tipo_badge_class

register = template.Library()


@register.filter
def noticia_alcance_label(value):
    return dict(Noticia.Alcance.choices).get(value, value or "")


@register.filter
def noticia_status_label(value):
    return dict(Noticia.Status.choices).get(value, value or "")


@register.filter
def noticia_alcance_badge(value):
    if value == Noticia.Alcance.GLOBAL:
        return "badge-type-user"
    return "badge-process"


@register.filter
def noticia_status_badge(value):
    if value == Noticia.Status.ACTIVO:
        return "badge-active"
    return "badge-inactive"


@register.filter
def noticia_tipo_badge(value):
    return tipo_badge_class(value)


@register.filter
def noticia_card_muted(noticia):
    return "manten" in (noticia.tipo or "").lower()
