from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.security.services import (
    email_confirmation,
    profile_routing,
    post_login_routing,
    security_session,
    session_idle,
    totp_reset,
    totp_utils,
)

User = get_user_model()


def _require_pending_user(request):
    user = security_session.get_pending_user(request)
    if user is None:
        messages.error(request, "Tu sesión de seguridad expiró. Ingresa de nuevo.")
        return None
    return user


def _finalize_access(request, user):
    profile = user.profile
    from apps.billing.services.subscription import expire_overdue_payments

    expire_overdue_payments(user)
    if not profile.is_security_complete:
        return redirect(profile_routing.resolve_security_step(profile))

    security_session.clear_security_session(request)
    login(request, user)
    session_idle.set_last_activity(request)
    profile.refresh_from_db()

    destination = post_login_routing.resolve_post_security_redirect(profile)
    if destination == reverse("noticias:feed"):
        post_login_routing.mark_primer_acceso_completado(profile)
        messages.success(
            request,
            "Bienvenido a BAKEBUDGE. Revisa las noticias del sistema "
            "para conocer los primeros pasos.",
        )
    elif destination == reverse("dashboard:home"):
        messages.success(request, "Bienvenido a tu panel.")
    else:
        messages.warning(
            request,
            "Tu cuenta aún no tiene acceso al panel. Contacta soporte si persiste.",
        )

    return redirect(destination)


@require_http_methods(["GET", "POST"])
def login_view(request):
    show_provisioned = request.GET.get("provisioned") == "1"

    if request.method == "GET" and request.GET.get(session_idle.IDLE_LOGOUT_QUERY_PARAM) == "1":
        messages.warning(request, "Sesión cerrada por inactividad.")

    if request.user.is_authenticated and request.user.profile.is_security_complete:
        if session_idle.should_relogin_at_login_gate(request):
            logout(request)
            messages.warning(request, "Sesión cerrada por inactividad.")
            return render(
                request,
                "security/login.html",
                {"show_provisioned": show_provisioned},
            )
        if request.user.profile.can_access_app:
            return redirect(
                post_login_routing.resolve_post_security_redirect(
                    request.user.profile
                )
            )
        return redirect("dashboard:access_denied")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Completa usuario y contraseña.")
            return render(
                request,
                "security/login.html",
                {"show_provisioned": show_provisioned},
            )

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return render(
                request,
                "security/login.html",
                {"show_provisioned": show_provisioned},
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(
                request,
                "Contraseña incorrecta. Si olvidaste tu contraseña, contacta soporte.",
            )
            return render(
                request,
                "security/login.html",
                {"show_provisioned": show_provisioned},
            )

        if not hasattr(user, "profile"):
            messages.error(request, "Tu perfil no está configurado. Contacta soporte.")
            return render(
                request,
                "security/login.html",
                {"show_provisioned": show_provisioned},
            )

        profile = user.profile
        from apps.billing.services.subscription import expire_overdue_payments

        expire_overdue_payments(user)
        next_url, error = profile_routing.validate_account_for_login(user, profile)
        if error:
            messages.error(request, error)
            return render(
                request,
                "security/login.html",
                {"show_provisioned": show_provisioned},
            )

        security_session.set_pending_user(request, user)
        security_session.set_totp_setup_mode(
            request, not profile.is_security_complete
        )

        if next_url == reverse("security:email_code"):
            email_confirmation.send_confirmation_email(user, profile)

        return redirect(next_url)

    return render(
        request,
        "security/login.html",
        {"show_provisioned": show_provisioned},
    )


@require_GET
def register_view(request):
    messages.info(
        request,
        "El registro público no está disponible. Solicita acceso desde contacto.",
    )
    return redirect("public_site:contacto")


@require_http_methods(["GET", "POST"])
def email_code_view(request):
    user = _require_pending_user(request)
    if user is None:
        return redirect("security:login")

    profile = user.profile
    if profile.email_confirmed:
        return redirect("security:totp_setup")

    if request.method == "POST":
        action = request.POST.get("action", "verify")

        if action == "resend":
            email_confirmation.send_confirmation_email(user, profile)
            messages.success(request, "Enviamos un nuevo código a tu correo.")
            return redirect("security:email_code")

        if action == "cancel":
            security_session.clear_security_session(request)
            return redirect("security:login")

        code = request.POST.get("code", "").strip()
        if email_confirmation.verify_email_code(profile, code):
            security_session.set_totp_setup_mode(request, True)
            return redirect("security:totp_setup")

        messages.error(request, "Código inválido o expirado")
        return render(
            request,
            "security/email_code.html",
            {"masked_email": email_confirmation.mask_email(user.email)},
        )

    if not profile.email_confirm_code or (
        profile.email_confirm_exp and profile.email_confirm_exp < timezone.now()
    ):
        email_confirmation.send_confirmation_email(user, profile)

    return render(
        request,
        "security/email_code.html",
        {"masked_email": email_confirmation.mask_email(user.email)},
    )


@require_GET
def totp_setup_view(request):
    user = _require_pending_user(request)
    if user is None:
        return redirect("security:login")

    profile = user.profile
    if not profile.email_confirmed:
        return redirect("security:email_code")

    if not profile.totp_secret:
        profile.totp_secret = totp_utils.generate_secret()
        profile.save(update_fields=["totp_secret"])

    uri = totp_utils.provisioning_uri(user, profile.totp_secret)
    return render(
        request,
        "security/totp_setup.html",
        {
            "totp_secret": profile.totp_secret,
            "qr_data_url": totp_utils.qr_code_data_url(uri),
        },
    )


@require_http_methods(["GET", "POST"])
def totp_view(request):
    user = _require_pending_user(request)
    if user is None:
        return redirect("security:login")

    profile = user.profile
    if request.GET.get("mode") == "setup":
        security_session.set_totp_setup_mode(request, True)
    setup_mode = security_session.is_totp_setup_mode(request) or request.GET.get(
        "mode"
    ) == "setup"

    if not profile.totp_secret:
        return redirect("security:totp_setup")

    if request.method == "POST":
        action = request.POST.get("action", "verify")

        if action == "cancel":
            security_session.clear_security_session(request)
            return redirect("security:login")

        code = request.POST.get("totp", "").strip()
        if not totp_utils.verify_totp(profile.totp_secret, code):
            messages.error(request, "Código de autenticación incorrecto")
            return render(
                request,
                "security/totp.html",
                {"setup_mode": setup_mode},
            )

        if setup_mode and not profile.tfa_verified:
            profile.tfa_verified = True
            profile.save(update_fields=["tfa_verified"])

        return _finalize_access(request, user)

    return render(
        request,
        "security/totp.html",
        {"setup_mode": setup_mode},
    )


@require_http_methods(["GET", "POST"])
def actualizar_2fa_view(request):
    user = _require_pending_user(request)
    if user is None:
        return redirect("security:login")

    if request.method == "POST":
        password = request.POST.get("password", "")
        auth_user = authenticate(
            request,
            username=user.username,
            password=password,
        )
        if auth_user is None:
            messages.error(request, "Contraseña incorrecta.")
            return render(request, "security/actualizar_2fa.html")

        totp_reset.reset_and_send_email(user, user.profile)
        security_session.set_totp_setup_mode(request, True)
        messages.info(
            request,
            "Reiniciamos tu 2FA. Verifica tu correo para continuar.",
        )
        return redirect("security:email_code")

    return render(request, "security/actualizar_2fa.html")


@require_GET
def cancel_view(request):
    security_session.clear_security_session(request)
    messages.info(request, "Proceso de seguridad cancelado.")
    return redirect("security:login")


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("public_site:home")
