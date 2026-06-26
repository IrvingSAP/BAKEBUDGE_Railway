"""Sesión parcial del wizard de seguridad (sin login completo hasta TOTP)."""

from django.contrib.auth import get_user_model

SESSION_PENDING_USER_KEY = "security_pending_user_id"
SESSION_TOTP_SETUP = "security_totp_setup"

User = get_user_model()


def set_pending_user(request, user) -> None:
    request.session[SESSION_PENDING_USER_KEY] = user.pk


def get_pending_user(request):
    user_id = request.session.get(SESSION_PENDING_USER_KEY)
    if not user_id:
        return None
    try:
        return User.objects.select_related("profile").get(pk=user_id)
    except User.DoesNotExist:
        clear_security_session(request)
        return None


def set_totp_setup_mode(request, enabled: bool = True) -> None:
    request.session[SESSION_TOTP_SETUP] = enabled


def is_totp_setup_mode(request) -> bool:
    return bool(request.session.get(SESSION_TOTP_SETUP))


def clear_security_session(request) -> None:
    request.session.pop(SESSION_PENDING_USER_KEY, None)
    request.session.pop(SESSION_TOTP_SETUP, None)
