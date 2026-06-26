from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render

from apps.accounts.services.cuenta_seguridad_helpers import (
    apply_cuenta_seguridad_change,
    empty_cuenta_seguridad_form,
    parse_cuenta_seguridad_post,
    validate_cuenta_seguridad_form,
)
from apps.accounts.services.perfil_helpers import (
    UNIDAD_CONTEO_CHOICES,
    UNIDAD_PESO_CHOICES,
    UNIDAD_VOLUMEN_CHOICES,
    apply_perfil_form,
    form_defaults_from_profile,
    monedas_for_select,
    parse_perfil_post,
    validate_perfil_form,
)
from apps.core.form_validation import form_error_context
from apps.security.decorators import app_access_required
from apps.security.services import security_session


def _perfil_context(request, form_data, **extra):
    profile = request.user.profile
    return {
        "form_data": form_data,
        "monedas": monedas_for_select(profile),
        "unidad_peso_choices": UNIDAD_PESO_CHOICES,
        "unidad_volumen_choices": UNIDAD_VOLUMEN_CHOICES,
        "unidad_conteo_choices": UNIDAD_CONTEO_CHOICES,
        **extra,
    }


@app_access_required
def perfil(request):
    profile = request.user.profile
    form_data = form_defaults_from_profile(profile)

    if request.method == "POST":
        form_data = parse_perfil_post(request)
        errors = {}
        validate_perfil_form(form_data, errors, profile=profile)

        if errors:
            return render(
                request,
                "accounts/perfil.html",
                _perfil_context(request, form_data, **form_error_context(errors)),
            )

        apply_perfil_form(profile, form_data)
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("accounts:perfil")

    return render(request, "accounts/perfil.html", _perfil_context(request, form_data))


@app_access_required
def cuenta_seguridad(request):
    user = request.user
    profile = user.profile
    form_data = empty_cuenta_seguridad_form()

    if not profile.is_active_account:
        messages.error(request, "Tu cuenta está temporalmente bloqueada. Intenta más tarde.")
        return redirect("accounts:perfil")

    if request.method == "POST":
        form_data = parse_cuenta_seguridad_post(request)
        errors = {}
        validate_cuenta_seguridad_form(form_data, errors, request=request, user=user)

        if errors:
            return render(
                request,
                "accounts/cuenta_seguridad.html",
                {"form_data": form_data, **form_error_context(errors)},
            )

        apply_cuenta_seguridad_change(user, profile, form_data["password_new"])
        logout(request)
        security_session.clear_security_session(request)
        messages.info(
            request,
            "Contraseña actualizada. Ingresa de nuevo y completa la verificación de correo y autenticador.",
        )
        return redirect("security:login")

    return render(
        request,
        "accounts/cuenta_seguridad.html",
        {"form_data": form_data},
    )
