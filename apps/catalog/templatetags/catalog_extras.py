from decimal import Decimal, InvalidOperation

from django import template

from apps.catalog.constants import Status

register = template.Library()

STATUS_LABELS = dict(Status.choices)
STATUS_BADGES = {
    Status.ACTIVO: "badge-active",
    Status.EN_PROCESO: "badge-draft",
    Status.INACTIVO: "badge-inactive",
}


@register.filter
def status_label(value):
    return STATUS_LABELS.get(value, value or "")


@register.filter
def status_badge(value):
    return STATUS_BADGES.get(value, "badge-draft")


@register.filter
def format_money(value, user):
    if value in (None, ""):
        return ""

    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    profile = getattr(user, "profile", None)
    moneda = getattr(profile, "moneda", None)
    simbolo = getattr(moneda, "simbolo", "$")
    decimales = getattr(moneda, "decimales", 2)

    if decimales < 0:
        decimales = 2

    return f"{simbolo} {amount:,.{decimales}f}"
