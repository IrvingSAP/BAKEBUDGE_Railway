from functools import wraps

from apps.catalog.decorators import catalog_access


def recipes_access(view_func):
    """Acceso a /app/recetas/ — requiere app + defaults de catálogo."""

    @catalog_access
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper
