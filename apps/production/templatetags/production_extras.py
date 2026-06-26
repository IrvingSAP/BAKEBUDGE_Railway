from django import template

from apps.production.constants import ESTADO_BADGES, Estado

register = template.Library()

ESTADO_LABELS = dict(Estado.choices)


@register.filter
def estado_label(value):
    return ESTADO_LABELS.get(value, value or "")


@register.filter
def estado_badge(value):
    return ESTADO_BADGES.get(value, "badge-draft")
