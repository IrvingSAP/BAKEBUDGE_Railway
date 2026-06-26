"""Autenticación por contraseña y bloqueos temporales."""

from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def authenticate_credentials(request, username: str, password: str):
    username = username.strip()
    user = authenticate(request, username=username, password=password)
    if user is not None:
        return user, None

    return None, "Contraseña incorrecta. Si olvidaste tu contraseña, contacta soporte."


def record_failed_login(profile) -> None:
    profile.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_MINUTES)
    profile.save(update_fields=["locked_until"])
