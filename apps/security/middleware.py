from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

from apps.security.services import session_idle


class AppIdleTimeoutMiddleware:
    """Cierra sesión tras inactividad en rutas /app/."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_enforce(request):
            if session_idle.is_idle_enforcement_required(request):
                return self._idle_logout_response(request)
            session_idle.set_last_activity(request)
        return self.get_response(request)

    def _should_enforce(self, request) -> bool:
        if not getattr(request.user, "is_authenticated", False):
            return False
        if not session_idle.is_app_path(request.path):
            return False
        return True

    def _idle_logout_response(self, request):
        logout(request)
        login_url = reverse("security:login")
        return redirect(f"{login_url}?{session_idle.IDLE_LOGOUT_QUERY_PARAM}=1")
