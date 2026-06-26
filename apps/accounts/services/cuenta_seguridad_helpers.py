"""Validación y aplicación del cambio de contraseña + reset 2FA desde /app/."""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.core.form_validation import form_error_context, required_field_message
from apps.security.services.totp_reset import reset_two_factor

CUENTA_SEGURIDAD_FIELD_LABELS = {
    "password_current": "Contraseña actual",
    "password_new": "Nueva contraseña",
    "password_confirm": "Confirmar nueva contraseña",
    "confirm_ack": "Confirmación",
}


def _required(field_name):
    return required_field_message(field_name, CUENTA_SEGURIDAD_FIELD_LABELS)


def empty_cuenta_seguridad_form():
    return {
        "password_current": "",
        "password_new": "",
        "password_confirm": "",
        "confirm_ack": False,
    }


def parse_cuenta_seguridad_post(request):
    return {
        "password_current": request.POST.get("password_current", ""),
        "password_new": request.POST.get("password_new", ""),
        "password_confirm": request.POST.get("password_confirm", ""),
        "confirm_ack": request.POST.get("confirm_ack") in {"1", "on"},
    }


def validate_cuenta_seguridad_form(form_data, errors, *, request, user):
    current = form_data.get("password_current") or ""
    if not current:
        errors["password_current"] = _required("password_current")
    else:
        auth_user = authenticate(
            request,
            username=user.username,
            password=current,
        )
        if auth_user is None:
            errors["password_current"] = "Contraseña actual incorrecta."

    password_new = form_data.get("password_new") or ""
    password_confirm = form_data.get("password_confirm") or ""

    if not password_new:
        errors["password_new"] = _required("password_new")
    elif len(password_new) < 8:
        errors["password_new"] = "La contraseña debe tener al menos 8 caracteres."
    elif user.check_password(password_new):
        errors["password_new"] = "La nueva contraseña no puede ser igual a la anterior."
    elif password_new.lower() == user.username.lower():
        errors["password_new"] = "La nueva contraseña no puede ser igual al nombre de usuario."
    else:
        try:
            validate_password(password_new, user=user)
        except ValidationError as exc:
            errors["password_new"] = " ".join(exc.messages)

    if not password_confirm:
        errors["password_confirm"] = _required("password_confirm")
    elif password_new and password_new != password_confirm:
        errors["password_confirm"] = "Las contraseñas no coinciden."

    if not form_data.get("confirm_ack"):
        errors["confirm_ack"] = (
            "Debes confirmar que entiendes las consecuencias del cambio de seguridad."
        )


def apply_cuenta_seguridad_change(user, profile, new_password):
    with transaction.atomic():
        user.set_password(new_password)
        user.save(update_fields=["password"])
        reset_two_factor(profile)


__all__ = [
    "apply_cuenta_seguridad_change",
    "empty_cuenta_seguridad_form",
    "form_error_context",
    "parse_cuenta_seguridad_post",
    "validate_cuenta_seguridad_form",
]
