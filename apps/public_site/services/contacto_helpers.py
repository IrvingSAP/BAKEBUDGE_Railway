"""Validación del formulario público de contacto."""

from django.core.validators import EmailValidator

MENSAJE_MIN_LEN = 10
MENSAJE_MAX_LEN = 5000

CONTACTO_FIELD_LABELS = {
    "nombre": "Nombre",
    "email": "Correo",
    "mensaje": "Mensaje",
}


def parse_contacto_post(request):
    return {
        "nombre": (request.POST.get("nombre") or "").strip(),
        "email": (request.POST.get("email") or "").strip(),
        "mensaje": (request.POST.get("mensaje") or "").strip(),
    }


def validate_contacto_form(form_data, errors):
    nombre = form_data.get("nombre") or ""
    if not nombre:
        errors["nombre"] = "El campo «Nombre» es obligatorio."
    elif len(nombre) > 150:
        errors["nombre"] = "El nombre no puede superar 150 caracteres."

    email = form_data.get("email") or ""
    if not email:
        errors["email"] = "El campo «Correo» es obligatorio."
    else:
        validator = EmailValidator(message="Ingresa un correo electrónico válido.")
        try:
            validator(email)
        except Exception:
            errors["email"] = "Ingresa un correo electrónico válido."

    mensaje = form_data.get("mensaje") or ""
    if not mensaje:
        errors["mensaje"] = "El campo «Mensaje» es obligatorio."
    elif len(mensaje) < MENSAJE_MIN_LEN:
        errors["mensaje"] = f"El mensaje debe tener al menos {MENSAJE_MIN_LEN} caracteres."
    elif len(mensaje) > MENSAJE_MAX_LEN:
        errors["mensaje"] = f"El mensaje no puede superar {MENSAJE_MAX_LEN} caracteres."


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
