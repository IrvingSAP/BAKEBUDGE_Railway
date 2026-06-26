"""Código de verificación por correo (6 dígitos, 5 min)."""

import secrets
from datetime import timedelta

from django.utils import timezone

from apps.core.services.email_delivery import send_transactional_email

CODE_TTL_MINUTES = 5
EMAIL_SUBJECT = "Código de verificación BAKEBUDGE"


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if not local:
        return email
    if len(local) <= 2:
        masked_local = f"{local[0]}***"
    else:
        masked_local = f"{local[0]}***{local[-1]}"
    return f"{masked_local}@{domain}"


def issue_email_code(profile) -> str:
    code = f"{secrets.randbelow(10**6):06d}"
    profile.email_confirm_code = code
    profile.email_confirm_exp = timezone.now() + timedelta(minutes=CODE_TTL_MINUTES)
    profile.save(update_fields=["email_confirm_code", "email_confirm_exp"])
    return code


def send_confirmation_email(user, profile) -> None:
    code = issue_email_code(profile)
    body = (
        f"Hola {user.username},\n\n"
        f"Tu código de verificación BAKEBUDGE es: {code}\n"
        f"Vence en {CODE_TTL_MINUTES} minutos.\n\n"
        "Si no solicitaste este código, ignora este mensaje."
    )
    send_transactional_email(to=user.email, subject=EMAIL_SUBJECT, body=body)


def verify_email_code(profile, code: str) -> bool:
    if not profile.email_confirm_code or not profile.email_confirm_exp:
        return False
    if timezone.now() > profile.email_confirm_exp:
        return False
    if profile.email_confirm_code != code.strip():
        return False

    profile.email_confirmed = True
    profile.email_confirm_code = None
    profile.email_confirm_exp = None
    profile.save(
        update_fields=[
            "email_confirmed",
            "email_confirm_code",
            "email_confirm_exp",
        ]
    )
    return True
