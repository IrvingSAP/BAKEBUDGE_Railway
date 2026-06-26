from django.contrib import messages
from django.shortcuts import redirect, render

from apps.public_site.models import MensajeContacto
from apps.public_site.services.contacto_helpers import (
    get_client_ip,
    parse_contacto_post,
    validate_contacto_form,
)


def home(request):
    """Landing pública — presentación BAKEBUDGE (todos los visitantes)."""
    return render(request, "public_site/home.html")


def servicios(request):
    """Página de servicios — detalle de capacidades de la plataforma."""
    return render(request, "public_site/servicios.html")


def contacto(request):
    """Formulario público de contacto — persiste MensajeContacto."""
    form_data = {"nombre": "", "email": "", "mensaje": ""}

    if request.method == "POST":
        form_data = parse_contacto_post(request)
        errors = {}
        validate_contacto_form(form_data, errors)

        if errors:
            first_error = next(iter(errors.values()))
            messages.error(request, first_error)
        else:
            MensajeContacto.objects.create(
                nombre=form_data["nombre"],
                email=form_data["email"],
                mensaje=form_data["mensaje"],
                ip_origen=get_client_ip(request),
            )
            messages.success(
                request,
                "Recibimos tu mensaje. Te responderemos en 24–48 h hábiles.",
            )
            return redirect("public_site:contacto")

    return render(
        request,
        "public_site/contacto.html",
        {"form_data": form_data},
    )
