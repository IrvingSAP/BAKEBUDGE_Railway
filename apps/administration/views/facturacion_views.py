from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from apps.administration.decorators import master_access
from apps.administration.services.facturacion_helpers import (
    apply_guardar_activar,
    form_defaults,
    get_standard_users,
    parse_form_post,
    serialize_form_data,
    validate_form,
    validate_owner,
)
from apps.billing.models import PaymentControl
from apps.core.form_validation import form_error_context
from apps.core.models import Moneda

User = get_user_model()


def _get_payment(pk):
    return get_object_or_404(
        PaymentControl.objects.select_related(
            "owner",
            "owner__profile",
            "moneda",
            "created_by",
            "updated_by",
        ),
        pk=pk,
    )


def _active_monedas():
    monedas = Moneda.objects.filter(activa=True).order_by("orden", "codigo")
    if monedas.exists():
        return monedas
    return Moneda.objects.order_by("orden", "codigo")


def _owner_preselect(request):
    owner_param = request.GET.get("owner")
    if not owner_param:
        return None
    try:
        owner_id = int(owner_param)
    except (TypeError, ValueError):
        return None
    return User.objects.filter(pk=owner_id).select_related("profile").first()


def _apply_form_to_payment(payment, form_data, acting_user):
    payment.modalidad = form_data["modalidad"]
    payment.estado = form_data["estado"]
    payment.start_date = form_data.get("start_date")
    payment.end_date = form_data.get("end_date")
    payment.plazo_de_gracia = form_data.get("plazo_de_gracia", 0)
    payment.payment_date = form_data.get("payment_date")
    payment.payment_method = form_data.get("payment_method") or ""
    monto = form_data.get("monto")
    payment.monto = monto if monto not in (None, "") else None
    moneda = form_data.get("moneda")
    payment.moneda_id = moneda if moneda else None
    payment.payment_voucher = form_data.get("payment_voucher", "")
    payment.other_data = form_data.get("other_data", "")
    payment.updated_by = acting_user


def _render_form(request, form_data, *, payment=None, provision_user=None, **extra):
    return render(
        request,
        "administration/facturacion/facturacion_form.html",
        {
            "form_data": serialize_form_data(form_data),
            "payment": payment,
            "standard_users": get_standard_users(),
            "monedas": _active_monedas(),
            "provision_user": provision_user,
            **extra,
        },
    )


@master_access
def facturacion_list(request):
    pagos = PaymentControl.objects.select_related(
        "owner",
        "owner__profile",
        "moneda",
    ).order_by("-payment_date", "-start_date", "-created_at")
    return render(
        request,
        "administration/facturacion/facturacion_list.html",
        {"pagos": pagos},
    )


@master_access
def facturacion_create(request):
    provision_user = _owner_preselect(request)
    form_data = form_defaults(owner_preselect=provision_user)

    if request.method == "POST":
        form_data = parse_form_post(request)
        activating = bool(request.POST.get("guardar_activar"))
        if activating:
            apply_guardar_activar(form_data)

        errors = {}
        owner = validate_owner(form_data.get("owner"), errors)
        validate_form(
            form_data,
            errors,
            owner_id=owner.pk if owner else None,
            activating=activating,
        )

        if errors:
            return _render_form(
                request,
                form_data,
                provision_user=owner or provision_user,
                **form_error_context(errors),
            )

        payment = PaymentControl(owner=owner, created_by=request.user, updated_by=request.user)
        _apply_form_to_payment(payment, form_data, request.user)
        payment.save()

        messages.success(
            request,
            f"Período de pago para «{owner.username}» creado correctamente.",
        )
        return redirect("administration:facturacion_list")

    return _render_form(request, form_data, provision_user=provision_user)


@master_access
def facturacion_edit(request, pk):
    payment = _get_payment(pk)
    form_data = form_defaults(payment)

    if request.method == "POST":
        form_data = parse_form_post(request, payment=payment)
        activating = bool(request.POST.get("guardar_activar"))
        if activating:
            apply_guardar_activar(form_data)

        errors = {}
        validate_form(
            form_data,
            errors,
            owner_id=payment.owner_id,
            excluding_pk=payment.pk,
            activating=activating or form_data.get("estado") == PaymentControl.Estado.ACTIVO,
        )

        if errors:
            return _render_form(
                request,
                form_data,
                payment=payment,
                **form_error_context(errors),
            )

        _apply_form_to_payment(payment, form_data, request.user)
        payment.save()
        messages.success(request, f"Período #{payment.pk} actualizado correctamente.")
        return redirect("administration:facturacion_list")

    return _render_form(request, form_data, payment=payment)


@master_access
def facturacion_accion(request, pk):
    payment = _get_payment(pk)

    if payment.estado == PaymentControl.Estado.CONSUMIDO:
        return render(
            request,
            "administration/facturacion/facturacion_accion.html",
            {
                "payment": payment,
                "can_act": False,
                "block_message": "No puedes modificar un período consumido — es histórico de auditoría.",
            },
        )

    if payment.estado == PaymentControl.Estado.SUSPENDIDO:
        return render(
            request,
            "administration/facturacion/facturacion_accion.html",
            {
                "payment": payment,
                "can_act": False,
                "block_message": "Este período ya está suspendido.",
            },
        )

    is_pendiente = payment.estado == PaymentControl.Estado.PENDIENTE

    if request.method == "POST":
        payment.estado = PaymentControl.Estado.SUSPENDIDO
        payment.updated_by = request.user
        payment.save(update_fields=["estado", "updated_by", "updated_at"])
        verb = "cancelado" if is_pendiente else "suspendido"
        messages.success(
            request,
            f"Período #{payment.pk} {verb} correctamente (estado=suspendido).",
        )
        return redirect("administration:facturacion_list")

    return render(
        request,
        "administration/facturacion/facturacion_accion.html",
        {
            "payment": payment,
            "can_act": True,
            "is_pendiente": is_pendiente,
        },
    )


@master_access
def facturacion_create_help(request):
    return render(
        request,
        "administration/facturacion/facturacion_create_help.html",
        {"monedas": _active_monedas()},
    )


@master_access
def facturacion_edit_help(request, pk):
    payment = _get_payment(pk)
    return render(
        request,
        "administration/facturacion/facturacion_edit_help.html",
        {"payment": payment},
    )
