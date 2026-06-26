"""Lógica de suscripción, vigencia y vencimiento de PaymentControl."""

import calendar
from datetime import date, timedelta

from django.utils import timezone

from apps.billing.models import PaymentControl


def add_months(source_date: date, months: int) -> date:
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def add_years(source_date: date, years: int) -> date:
    try:
        return source_date.replace(year=source_date.year + years)
    except ValueError:
        return source_date.replace(year=source_date.year + years, day=28)


def suggest_end_date(start_date: date, modalidad: str) -> date:
    if modalidad == PaymentControl.Modalidad.ANUAL:
        return add_years(start_date, 1)
    return add_months(start_date, 1)


def effective_end_date(payment) -> date | None:
    if not payment.end_date:
        return None
    grace = payment.plazo_de_gracia or 0
    return payment.end_date + timedelta(days=grace)


def is_payment_vigente(payment, *, on_date: date | None = None) -> bool:
    if payment.estado != PaymentControl.Estado.ACTIVO:
        return False
    if not payment.start_date or not payment.end_date:
        return False
    today = on_date or timezone.localdate()
    end = effective_end_date(payment)
    if end is None:
        return False
    return payment.start_date <= today <= end


def is_payment_expired(payment, *, on_date: date | None = None) -> bool:
    end = effective_end_date(payment)
    if end is None:
        return False
    today = on_date or timezone.localdate()
    return today > end


def user_has_active_subscription(user) -> bool:
    payments = PaymentControl.objects.filter(
        owner=user,
        estado=PaymentControl.Estado.ACTIVO,
    )
    return any(is_payment_vigente(payment) for payment in payments)


def owner_has_active_payment(owner_id, *, excluding_pk=None) -> bool:
    qs = PaymentControl.objects.filter(
        owner_id=owner_id,
        estado=PaymentControl.Estado.ACTIVO,
    )
    if excluding_pk:
        qs = qs.exclude(pk=excluding_pk)
    return qs.exists()


def expire_overdue_payments(user, *, acting_user=None) -> int:
    """Marca como consumido los períodos activos cuya fecha efectiva ya venció."""
    today = timezone.localdate()
    updated = 0
    payments = PaymentControl.objects.filter(
        owner=user,
        estado=PaymentControl.Estado.ACTIVO,
    )
    for payment in payments:
        if not is_payment_expired(payment, on_date=today):
            continue
        payment.estado = PaymentControl.Estado.CONSUMIDO
        if acting_user:
            payment.updated_by = acting_user
        payment.save(update_fields=["estado", "updated_by", "updated_at"])
        updated += 1
    return updated
