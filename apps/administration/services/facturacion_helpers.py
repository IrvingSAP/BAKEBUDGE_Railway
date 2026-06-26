"""Utilidades de validación para formularios de PaymentControl."""

from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile
from apps.billing.models import PaymentControl
from apps.billing.services.subscription import owner_has_active_payment, suggest_end_date
from apps.core.models import Moneda

User = get_user_model()

FACTURACION_FIELD_LABELS = {
    "owner": "Usuario (owner)",
    "modalidad": "Modalidad",
    "estado": "Estado",
    "start_date": "Fecha inicio",
    "end_date": "Fecha fin",
    "payment_date": "Fecha de pago",
    "payment_method": "Método de pago",
    "monto": "Monto",
    "moneda": "Moneda",
    "payment_voucher": "Comprobante / referencia",
    "other_data": "Otros datos",
    "plazo_de_gracia": "Plazo de gracia",
}


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        from datetime import date

        return date.fromisoformat(value)
    except ValueError:
        return None


def get_standard_users():
    return (
        User.objects.filter(profile__user_type=UserProfile.UserType.USER)
        .select_related("profile")
        .order_by("username")
    )


def validate_owner(owner_id, errors):
    if not owner_id:
        errors["owner"] = "El campo «Usuario (owner)» es obligatorio."
        return None

    try:
        owner_id = int(owner_id)
    except (TypeError, ValueError):
        errors["owner"] = "Selecciona un usuario válido."
        return None

    owner = User.objects.filter(pk=owner_id).select_related("profile").first()
    if not owner:
        errors["owner"] = "El usuario seleccionado no existe."
        return None
    if owner.profile.user_type != UserProfile.UserType.USER:
        errors["owner"] = "Solo usuarios tipo User pueden tener períodos de pago."
        return None
    return owner


def validate_activation_fields(form_data, errors, *, owner_id, excluding_pk=None):
    payment_date = form_data.get("payment_date")
    if not payment_date:
        errors["payment_date"] = "La fecha de pago es obligatoria al activar."

    payment_method = form_data.get("payment_method") or ""
    if not payment_method:
        errors["payment_method"] = "El método de pago es obligatorio al activar."
    elif payment_method not in dict(PaymentControl.PaymentMethod.choices):
        errors["payment_method"] = "Selecciona un método de pago válido."

    monto_raw = form_data.get("monto")
    if monto_raw in (None, ""):
        errors["monto"] = "El monto es obligatorio al activar."
    else:
        try:
            monto = Decimal(str(monto_raw))
            if monto <= 0:
                errors["monto"] = "El monto debe ser mayor que 0."
            else:
                form_data["monto"] = monto
        except (InvalidOperation, TypeError):
            errors["monto"] = "Ingresa un monto válido."

    moneda_codigo = (form_data.get("moneda") or "").strip().upper()
    form_data["moneda"] = moneda_codigo
    if not moneda_codigo:
        errors["moneda"] = "La moneda es obligatoria al activar."
    elif not Moneda.objects.filter(codigo=moneda_codigo).exists():
        errors["moneda"] = f"La moneda «{moneda_codigo}» no existe."

    start_date = form_data.get("start_date")
    if not start_date:
        errors["start_date"] = "La fecha inicio es obligatoria al activar."

    end_date = form_data.get("end_date")
    if start_date and not end_date:
        form_data["end_date"] = suggest_end_date(start_date, form_data.get("modalidad"))

    if start_date and form_data.get("end_date") and form_data["end_date"] < start_date:
        errors["end_date"] = "La fecha fin no puede ser anterior a la fecha inicio."

    if owner_id and owner_has_active_payment(owner_id, excluding_pk=excluding_pk):
        errors["estado"] = "Este usuario ya tiene un período activo. Suspende el anterior antes de activar otro."


def validate_plazo_de_gracia(form_data, errors):
    raw = form_data.get("plazo_de_gracia")
    if raw in (None, ""):
        form_data["plazo_de_gracia"] = 0
        return
    try:
        days = int(raw)
    except (TypeError, ValueError):
        errors["plazo_de_gracia"] = "Ingresa un número entero válido en «Plazo de gracia»."
        return
    if days < 0 or days > 30:
        errors["plazo_de_gracia"] = "El plazo de gracia debe estar entre 0 y 30 días."
    else:
        form_data["plazo_de_gracia"] = days


def parse_form_post(request, *, payment=None):
    form_data = {
        "owner": request.POST.get("owner", payment.owner_id if payment else ""),
        "modalidad": request.POST.get("modalidad", payment.modalidad if payment else PaymentControl.Modalidad.MENSUAL),
        "estado": request.POST.get("estado", payment.estado if payment else PaymentControl.Estado.PENDIENTE),
        "start_date": parse_date(request.POST.get("start_date")),
        "end_date": parse_date(request.POST.get("end_date")),
        "plazo_de_gracia": request.POST.get(
            "plazo_de_gracia",
            str(payment.plazo_de_gracia) if payment else "0",
        ),
        "payment_date": parse_date(request.POST.get("payment_date")),
        "payment_method": request.POST.get("payment_method", payment.payment_method if payment else ""),
        "monto": request.POST.get("monto", str(payment.monto) if payment and payment.monto is not None else ""),
        "moneda": request.POST.get("moneda", payment.moneda_id if payment and payment.moneda_id else ""),
        "payment_voucher": request.POST.get("payment_voucher", payment.payment_voucher if payment else "").strip(),
        "other_data": request.POST.get("other_data", payment.other_data if payment else "").strip(),
    }
    return form_data


def serialize_form_data(form_data):
    result = dict(form_data)
    for key in ("start_date", "end_date", "payment_date"):
        value = result.get(key)
        if value and hasattr(value, "isoformat"):
            result[key] = value.isoformat()
    if result.get("monto") is not None and not isinstance(result["monto"], str):
        result["monto"] = str(result["monto"])
    if result.get("owner") not in (None, ""):
        result["owner"] = str(result["owner"])
    if result.get("plazo_de_gracia") is not None and not isinstance(result["plazo_de_gracia"], str):
        result["plazo_de_gracia"] = str(result["plazo_de_gracia"])
    return result


def apply_guardar_activar(form_data):
    form_data["estado"] = PaymentControl.Estado.ACTIVO


def validate_form(form_data, errors, *, owner_id=None, excluding_pk=None, activating=False):
    modalidad = form_data.get("modalidad") or ""
    if modalidad not in dict(PaymentControl.Modalidad.choices):
        errors["modalidad"] = "Selecciona una modalidad válida."

    estado = form_data.get("estado") or ""
    if estado not in dict(PaymentControl.Estado.choices):
        errors["estado"] = "Selecciona un estado válido."

    if activating or estado == PaymentControl.Estado.ACTIVO:
        validate_activation_fields(form_data, errors, owner_id=owner_id, excluding_pk=excluding_pk)

    if form_data.get("start_date") and form_data.get("end_date"):
        if form_data["end_date"] < form_data["start_date"]:
            errors["end_date"] = "La fecha fin no puede ser anterior a la fecha inicio."

    if form_data.get("monto") not in (None, ""):
        try:
            monto = Decimal(str(form_data["monto"]))
            if monto < 0:
                errors["monto"] = "El monto no puede ser negativo."
            else:
                form_data["monto"] = monto
        except (InvalidOperation, TypeError):
            errors["monto"] = "Ingresa un monto válido."

    moneda_codigo = (form_data.get("moneda") or "").strip().upper()
    if moneda_codigo:
        form_data["moneda"] = moneda_codigo
        if not Moneda.objects.filter(codigo=moneda_codigo).exists():
            errors["moneda"] = f"La moneda «{moneda_codigo}» no existe."

    payment_method = form_data.get("payment_method") or ""
    if payment_method and payment_method not in dict(PaymentControl.PaymentMethod.choices):
        errors["payment_method"] = "Selecciona un método de pago válido."

    validate_plazo_de_gracia(form_data, errors)


def form_defaults(payment=None, *, owner_preselect=None):
    if payment:
        return {
            "owner": str(payment.owner_id),
            "modalidad": payment.modalidad,
            "estado": payment.estado,
            "start_date": payment.start_date.isoformat() if payment.start_date else "",
            "end_date": payment.end_date.isoformat() if payment.end_date else "",
            "plazo_de_gracia": str(payment.plazo_de_gracia),
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else "",
            "payment_method": payment.payment_method,
            "monto": str(payment.monto) if payment.monto is not None else "",
            "moneda": payment.moneda_id or "",
            "payment_voucher": payment.payment_voucher,
            "other_data": payment.other_data,
        }

    default_moneda = Moneda.objects.filter(activa=True).order_by("orden", "codigo").first()
    return {
        "owner": str(owner_preselect.pk) if owner_preselect else "",
        "modalidad": PaymentControl.Modalidad.MENSUAL,
        "estado": PaymentControl.Estado.PENDIENTE,
        "start_date": "",
        "end_date": "",
        "plazo_de_gracia": "0",
        "payment_date": "",
        "payment_method": "",
        "monto": "",
        "moneda": default_moneda.codigo if default_moneda else "COP",
        "payment_voucher": "",
        "other_data": "",
    }
