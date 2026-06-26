"""Producción — Railway, Gunicorn, WhiteNoise, Resend (Anymail)."""

import os

from .base import *  # noqa: F403

DEBUG = False

# Railway termina TLS en el proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        f"https://{host}"
        for host in ALLOWED_HOSTS
        if host and host not in ("*", "localhost", "127.0.0.1")
    ]

# Dominio público que Railway inyecta (evita DisallowedHost si ALLOWED_HOSTS no se actualizó)
_railway_public = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_public and _railway_public not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, _railway_public]
    _origin = f"https://{_railway_public}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, _origin]

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

if EMAIL_DELIVERY == "console":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    INSTALLED_APPS += ["anymail"]
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {
        "RESEND_API_KEY": RESEND_API_KEY,
    }
