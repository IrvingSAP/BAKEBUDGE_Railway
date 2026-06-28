"""Control de inactividad en la zona /app/."""

from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

SESSION_LAST_ACTIVITY_KEY = "app_last_activity_at"
IDLE_LOGOUT_QUERY_PARAM = "idle"


def app_idle_timeout() -> timedelta:
    seconds = getattr(settings, "APP_IDLE_TIMEOUT_SECONDS", 40 * 60)
    return timedelta(seconds=seconds)


def is_app_path(path: str) -> bool:
    return path == "/app" or path.startswith("/app/")


def parse_last_activity(raw) -> datetime | None:
    if not raw:
        return None
    if isinstance(raw, datetime):
        value = raw
    else:
        try:
            value = datetime.fromisoformat(str(raw))
        except (TypeError, ValueError):
            return None
    if timezone.is_naive(value):
        return timezone.make_aware(value, timezone.get_current_timezone())
    return value


def get_last_activity(request) -> datetime | None:
    return parse_last_activity(request.session.get(SESSION_LAST_ACTIVITY_KEY))


def set_last_activity(request, moment: datetime | None = None) -> None:
    when = moment or timezone.now()
    request.session[SESSION_LAST_ACTIVITY_KEY] = when.isoformat()


def is_idle_expired(request) -> bool:
    last = get_last_activity(request)
    if last is None:
        return False
    return timezone.now() - last > app_idle_timeout()


def should_relogin_at_login_gate(request) -> bool:
    """True si /ingresar/ no debe saltar el formulario (sesión vieja o inactiva)."""
    last = get_last_activity(request)
    if last is None:
        return True
    return timezone.now() - last > app_idle_timeout()


def is_idle_enforcement_required(request) -> bool:
    """True si /app/ debe cerrar sesión (sin marca o inactividad > timeout)."""
    last = get_last_activity(request)
    if last is None:
        return True
    return timezone.now() - last > app_idle_timeout()
