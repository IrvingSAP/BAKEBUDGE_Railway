"""Decoradores de acceso a la zona privada /app/."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.security.services import profile_routing


def app_access_required(view_func):
    @login_required(login_url="/ingresar/")
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = request.user.profile

        if not profile.is_security_complete:
            return redirect(profile_routing.resolve_security_step(profile))

        if not profile.can_access_app:
            return redirect("dashboard:access_denied")

        return view_func(request, *args, **kwargs)

    return wrapper
