"""Desarrollo local — lee .env con DEBUG=True y correo en consola."""

from .base import *  # noqa: F403

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
