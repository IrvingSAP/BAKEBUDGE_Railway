from apps.recipes.views.help_views import (
    receta_create_help,
    receta_edit_help,
    recetaversion_create_help,
    recetaversion_edit_help,
)
from apps.recipes.views.receta_views import (
    receta_costos,
    receta_create,
    receta_delete,
    receta_edit,
    receta_list,
)
from apps.recipes.views.version_views import (
    recetaversion_create,
    recetaversion_detail,
    recetaversion_edit,
    recetaversion_list,
)

__all__ = [
    "receta_list",
    "receta_create",
    "receta_create_help",
    "receta_edit",
    "receta_edit_help",
    "receta_delete",
    "receta_costos",
    "recetaversion_edit",
    "recetaversion_edit_help",
    "recetaversion_create",
    "recetaversion_create_help",
    "recetaversion_list",
    "recetaversion_detail",
]
