import re

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.administration.decorators import master_access
from apps.administration.services.usuario_helpers import (
    can_deactivate_user,
    can_demote_master,
    mask_totp_secret,
)
from apps.core.form_validation import form_error_context, required_field_message
from apps.core.models import Moneda
from apps.security.services import email_confirmation
from apps.security.services.totp_reset import reset_two_factor

User = get_user_model()

USERNAME_PATTERN = re.compile(r"^\S+$")

USUARIO_FIELD_LABELS = {
    "username": "Usuario",
    "email": "Correo",
    "password": "Contraseña",
    "password_confirm": "Confirmar contraseña",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "is_active": "Cuenta activa",
    "nombre_negocio": "Nombre del negocio",
    "user_type": "Tipo de usuario",
    "moneda": "Moneda",
    "status": "Estado cuenta",
    "email_confirmed": "Correo verificado",
    "tfa_verified": "2FA completado",
}


def _required(field_name):
    return required_field_message(field_name, USUARIO_FIELD_LABELS)


def _parse_bool(value):
    return value in {"1", "true", "on", "si", "sí"}


def _get_managed_user(pk):
    return get_object_or_404(User.objects.select_related("profile", "profile__moneda"), pk=pk)


def _active_monedas():
    monedas = Moneda.objects.filter(activa=True).order_by("orden", "codigo")
    if monedas.exists():
        return monedas
    return Moneda.objects.order_by("orden", "codigo")


def _form_defaults(managed_user=None):
    if managed_user is None:
        default_moneda = _active_monedas().first()
        return {
            "username": "",
            "email": "",
            "password": "",
            "password_confirm": "",
            "first_name": "",
            "last_name": "",
            "is_active": True,
            "nombre_negocio": "",
            "user_type": UserProfile.UserType.USER,
            "moneda": default_moneda.codigo if default_moneda else "COP",
            "status": UserProfile.Status.ACTIVO,
        }

    profile = managed_user.profile
    return {
        "username": managed_user.username,
        "email": managed_user.email,
        "first_name": managed_user.first_name,
        "last_name": managed_user.last_name,
        "is_active": managed_user.is_active,
        "nombre_negocio": profile.nombre_negocio,
        "user_type": profile.user_type,
        "moneda": profile.moneda_id,
        "status": profile.status,
    }


def _validate_account_fields(form_data, errors, *, managed_user=None, require_password=False):
    username = (form_data.get("username") or "").strip()
    form_data["username"] = username

    if not username:
        errors["username"] = _required("username")
    elif len(username) > 150:
        errors["username"] = "El usuario no puede superar 150 caracteres."
    elif not USERNAME_PATTERN.match(username):
        errors["username"] = "El usuario no puede contener espacios."
    else:
        qs = User.objects.filter(username__iexact=username)
        if managed_user:
            qs = qs.exclude(pk=managed_user.pk)
        if qs.exists():
            errors["username"] = f"Ya existe un usuario con nombre «{username}»."

    email = (form_data.get("email") or "").strip()
    form_data["email"] = email

    if not email:
        errors["email"] = _required("email")
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Ingresa un correo electrónico válido."
        else:
            qs = User.objects.filter(email__iexact=email)
            if managed_user:
                qs = qs.exclude(pk=managed_user.pk)
            if qs.exists():
                errors["email"] = f"Ya existe un usuario con correo «{email}»."

    if require_password:
        password = form_data.get("password") or ""
        password_confirm = form_data.get("password_confirm") or ""

        if not password:
            errors["password"] = _required("password")
        elif len(password) < 8:
            errors["password"] = "La contraseña debe tener al menos 8 caracteres."
        else:
            candidate = User(
                username=username or "user",
                email=email or "user@example.com",
            )
            try:
                validate_password(password, user=candidate)
            except ValidationError as exc:
                errors["password"] = " ".join(exc.messages)

        if not password_confirm:
            errors["password_confirm"] = _required("password_confirm")
        elif password and password != password_confirm:
            errors["password_confirm"] = "Las contraseñas no coinciden."


def _validate_profile_fields(form_data, errors, *, managed_user=None):
    user_type = form_data.get("user_type") or ""
    if user_type not in {UserProfile.UserType.MASTER, UserProfile.UserType.USER}:
        errors["user_type"] = "Selecciona un tipo de usuario válido."
    elif managed_user:
        ok, message = can_demote_master(managed_user, user_type)
        if not ok:
            errors["user_type"] = message

    moneda_codigo = (form_data.get("moneda") or "").strip().upper()
    form_data["moneda"] = moneda_codigo
    if not moneda_codigo:
        errors["moneda"] = _required("moneda")
    elif not Moneda.objects.filter(codigo=moneda_codigo).exists():
        errors["moneda"] = f"La moneda «{moneda_codigo}» no existe."

    status = form_data.get("status") or ""
    if status not in {UserProfile.Status.ACTIVO, UserProfile.Status.INACTIVO}:
        errors["status"] = "Selecciona un estado de cuenta válido."


def _apply_guardar_activar(form_data, request):
    if request.POST.get("guardar_activar"):
        form_data["status"] = UserProfile.Status.ACTIVO
        form_data["is_active"] = True


def _parse_form_post(request, *, managed_user=None, include_password=False):
    form_data = {
        "username": request.POST.get("username", ""),
        "email": request.POST.get("email", ""),
        "first_name": request.POST.get("first_name", "").strip(),
        "last_name": request.POST.get("last_name", "").strip(),
        "is_active": _parse_bool(request.POST.get("is_active", "")),
        "nombre_negocio": request.POST.get("nombre_negocio", "").strip(),
        "user_type": request.POST.get("user_type", UserProfile.UserType.USER),
        "moneda": request.POST.get("moneda", ""),
        "status": request.POST.get("status", UserProfile.Status.ACTIVO),
    }
    if include_password:
        form_data["password"] = request.POST.get("password", "")
        form_data["password_confirm"] = request.POST.get("password_confirm", "")
    _apply_guardar_activar(form_data, request)
    return form_data


def _render_form(request, form_data, *, managed_user=None, **extra):
    context = {
        "form_data": form_data,
        "monedas": _active_monedas(),
        **extra,
    }
    if managed_user:
        context["managed_user"] = managed_user
    return render(request, "administration/usuarios/usuario_form.html", context)


@master_access
def usuario_list(request):
    usuarios = User.objects.select_related("profile", "profile__moneda").order_by("-date_joined")
    return render(
        request,
        "administration/usuarios/usuario_list.html",
        {"usuarios": usuarios},
    )


@master_access
def usuario_create(request):
    form_data = _form_defaults()

    if request.method == "POST":
        form_data = _parse_form_post(request, include_password=True)
        errors = {}
        _validate_account_fields(form_data, errors, require_password=True)
        _validate_profile_fields(form_data, errors)

        if errors:
            return _render_form(request, form_data, **form_error_context(errors))

        with transaction.atomic():
            user = User.objects.create_user(
                username=form_data["username"],
                email=form_data["email"],
                password=form_data["password"],
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                is_active=form_data["is_active"],
            )
            profile = user.profile
            profile.nombre_negocio = form_data["nombre_negocio"]
            profile.user_type = form_data["user_type"]
            profile.moneda_id = form_data["moneda"]
            profile.status = form_data["status"]
            profile.save()

        messages.success(request, f"Usuario «{user.username}» creado correctamente.")
        if profile.user_type == UserProfile.UserType.USER:
            url = f"{reverse('administration:facturacion_create')}?owner={user.pk}"
            return redirect(url)
        return redirect("administration:usuario_list")

    return _render_form(request, form_data)


@master_access
def usuario_edit(request, pk):
    managed_user = _get_managed_user(pk)
    form_data = _form_defaults(managed_user)

    if request.method == "POST":
        form_data = _parse_form_post(request, managed_user=managed_user)
        errors = {}
        _validate_account_fields(form_data, errors, managed_user=managed_user)
        _validate_profile_fields(form_data, errors, managed_user=managed_user)

        if errors:
            return _render_form(
                request,
                form_data,
                managed_user=managed_user,
                **form_error_context(errors),
            )

        managed_user.username = form_data["username"]
        managed_user.email = form_data["email"]
        managed_user.first_name = form_data["first_name"]
        managed_user.last_name = form_data["last_name"]
        managed_user.is_active = form_data["is_active"]
        managed_user.save()

        profile = managed_user.profile
        profile.nombre_negocio = form_data["nombre_negocio"]
        profile.user_type = form_data["user_type"]
        profile.moneda_id = form_data["moneda"]
        profile.status = form_data["status"]
        profile.save()

        messages.success(request, f"Usuario «{managed_user.username}» actualizado correctamente.")
        return redirect("administration:usuario_list")

    return _render_form(request, form_data, managed_user=managed_user)


@master_access
def usuario_password(request, pk):
    managed_user = _get_managed_user(pk)

    if request.method == "POST":
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")
        errors = {}

        if not password:
            errors["password"] = _required("password")
        elif len(password) < 8:
            errors["password"] = "La contraseña debe tener al menos 8 caracteres."
        else:
            try:
                validate_password(password, user=managed_user)
            except ValidationError as exc:
                errors["password"] = " ".join(exc.messages)

        if not password_confirm:
            errors["password_confirm"] = _required("password_confirm")
        elif password and password != password_confirm:
            errors["password_confirm"] = "Las contraseñas no coinciden."

        if errors:
            return render(
                request,
                "administration/usuarios/usuario_password.html",
                {"managed_user": managed_user, **form_error_context(errors)},
            )

        managed_user.set_password(password)
        managed_user.save()
        messages.success(
            request,
            f"Contraseña de «{managed_user.username}» actualizada correctamente.",
        )
        return redirect("administration:usuario_list")

    return render(request, "administration/usuarios/usuario_password.html", {"managed_user": managed_user})


@master_access
def usuario_seguridad(request, pk):
    managed_user = _get_managed_user(pk)
    profile = managed_user.profile

    if request.method == "POST":
        if request.POST.get("reset_2fa"):
            reset_two_factor(profile)
            messages.success(request, f"2FA de «{managed_user.username}» restablecido correctamente.")
            return redirect("administration:usuario_seguridad", pk=pk)

        if request.POST.get("reenviar_codigo"):
            email_confirmation.send_confirmation_email(managed_user, profile)
            messages.success(
                request,
                f"Código de verificación enviado a «{managed_user.email}».",
            )
            return redirect("administration:usuario_seguridad", pk=pk)

        profile.email_confirmed = _parse_bool(request.POST.get("email_confirmed", ""))
        profile.tfa_verified = _parse_bool(request.POST.get("tfa_verified", ""))
        profile.save(update_fields=["email_confirmed", "tfa_verified"])
        messages.success(request, "Cambios de seguridad guardados correctamente.")
        return redirect("administration:usuario_seguridad", pk=pk)

    return render(
        request,
        "administration/usuarios/usuario_seguridad.html",
        {
            "managed_user": managed_user,
            "totp_secret_masked": mask_totp_secret(profile.totp_secret),
        },
    )


@master_access
def usuario_deactivate(request, pk):
    managed_user = _get_managed_user(pk)
    profile = managed_user.profile
    can_deactivate, block_message = can_deactivate_user(managed_user, request.user)

    if request.method == "POST":
        if not can_deactivate:
            return render(
                request,
                "administration/usuarios/usuario_deactivate.html",
                {
                    "managed_user": managed_user,
                    "can_deactivate": False,
                    "block_message": block_message,
                    "error_tipo": "ER",
                    "message_modal": block_message,
                },
            )

        profile.status = UserProfile.Status.INACTIVO
        profile.save(update_fields=["status"])
        managed_user.is_active = False
        managed_user.save(update_fields=["is_active"])

        messages.success(request, f"Usuario «{managed_user.username}» desactivado correctamente.")
        return redirect("administration:usuario_list")

    return render(
        request,
        "administration/usuarios/usuario_deactivate.html",
        {
            "managed_user": managed_user,
            "can_deactivate": can_deactivate,
            "block_message": block_message,
        },
    )


@master_access
def usuario_create_help(request):
    return render(
        request,
        "administration/usuarios/usuario_create_help.html",
        {"monedas": _active_monedas()},
    )


@master_access
def usuario_edit_help(request, pk):
    managed_user = _get_managed_user(pk)
    return render(
        request,
        "administration/usuarios/usuario_edit_help.html",
        {"managed_user": managed_user, "monedas": _active_monedas()},
    )
