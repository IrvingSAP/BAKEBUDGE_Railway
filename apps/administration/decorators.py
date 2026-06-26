from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from apps.security.decorators import app_access_required


def master_access(view_func):
    @app_access_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile = request.user.profile
        if not profile.is_master:
            messages.error(request, "Solo usuarios Master pueden acceder a Administración.")
            return redirect("dashboard:access_denied")
        return view_func(request, *args, **kwargs)

    return wrapper
