from functools import wraps

from apps.catalog.services.defaults import ensure_user_catalog_defaults
from apps.security.decorators import app_access_required


def catalog_access(view_func):
    @app_access_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ensure_user_catalog_defaults(request.user)
        return view_func(request, *args, **kwargs)

    return wrapper
