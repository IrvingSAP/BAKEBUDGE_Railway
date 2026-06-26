from functools import wraps

from apps.production.decorators import production_access


def analytics_access(view_func):
    """Acceso a /app/estadisticas/ — requiere catálogo, recetas y producción."""

    @production_access
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper
