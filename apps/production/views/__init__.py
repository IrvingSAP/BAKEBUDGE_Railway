from apps.production.views.help_views import orden_create_help, orden_edit_help
from apps.production.views.orden_views import (
    orden_create,
    orden_detail,
    orden_edit,
    orden_list,
)

__all__ = [
    "orden_list",
    "orden_create",
    "orden_create_help",
    "orden_edit",
    "orden_edit_help",
    "orden_detail",
]
