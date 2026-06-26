"""Routing del wizard según flags de UserProfile."""

from django.urls import reverse


def resolve_security_step(profile) -> str:
    if profile.is_security_complete:
        return reverse("security:totp")
    if not profile.email_confirmed:
        return reverse("security:email_code")
    if not profile.tfa_verified or not profile.totp_secret:
        return reverse("security:totp_setup")
    return reverse("security:totp_setup")


def validate_account_for_login(user, profile):
    if not user.email:
        return None, "Tu cuenta no tiene correo configurado. Contacta soporte."
    if not profile.is_active_account:
        return None, "Tu cuenta está temporalmente bloqueada. Intenta más tarde."
    return resolve_security_step(profile), None
