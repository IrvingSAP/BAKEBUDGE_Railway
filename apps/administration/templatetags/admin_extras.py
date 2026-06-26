from django import template

from apps.accounts.models import UserProfile
from apps.billing.models import PaymentControl
from apps.public_site.models import MensajeContacto

register = template.Library()

USER_TYPE_BADGES = {
    UserProfile.UserType.MASTER: "badge-type-master",
    UserProfile.UserType.USER: "badge-type-user",
}

PAYMENT_ESTADO_BADGES = {
    PaymentControl.Estado.PENDIENTE: "badge-draft",
    PaymentControl.Estado.ACTIVO: "badge-active",
    PaymentControl.Estado.SUSPENDIDO: "badge-inactive",
    PaymentControl.Estado.CONSUMIDO: "badge-system",
}

MENSAJE_ESTADO_BADGES = {
    MensajeContacto.Estado.PENDIENTE: "badge-draft",
    MensajeContacto.Estado.LEIDO: "badge-active",
}


@register.filter
def user_type_label(value):
    return dict(UserProfile.UserType.choices).get(value, value or "")


@register.filter
def user_type_badge(value):
    return USER_TYPE_BADGES.get(value, "badge-type-user")


@register.filter
def payment_estado_label(value):
    return dict(PaymentControl.Estado.choices).get(value, value or "")


@register.filter
def payment_estado_badge(value):
    return PAYMENT_ESTADO_BADGES.get(value, "badge-draft")


@register.filter
def payment_modalidad_label(value):
    return dict(PaymentControl.Modalidad.choices).get(value, value or "")


@register.filter
def payment_method_label(payment):
    if not payment.payment_method:
        return "—"
    return dict(PaymentControl.PaymentMethod.choices).get(payment.payment_method, payment.payment_method)


@register.filter
def mensaje_estado_label(value):
    return dict(MensajeContacto.Estado.choices).get(value, value or "")


@register.filter
def mensaje_estado_badge(value):
    return MENSAJE_ESTADO_BADGES.get(value, "badge-draft")
