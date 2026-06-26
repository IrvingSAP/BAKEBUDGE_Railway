from functools import wraps

from apps.recipes.decorators import recipes_access


def production_access(view_func):
    """Acceso a /app/produccion/ — requiere catálogo, recetas y suscripción activa."""

    @recipes_access
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper
