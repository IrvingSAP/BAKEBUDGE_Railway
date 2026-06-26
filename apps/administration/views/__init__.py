from .mensajecontacto_views import (
    mensajecontacto_delete,
    mensajecontacto_detail,
    mensajecontacto_list,
)

from .noticia_views import (
    noticia_copy,
    noticia_create,
    noticia_deactivate,
    noticia_edit,
    noticia_list,
)

from .facturacion_views import (

    facturacion_accion,

    facturacion_create,

    facturacion_create_help,

    facturacion_edit,

    facturacion_edit_help,

    facturacion_list,

)

from .moneda_views import moneda_create, moneda_delete, moneda_edit, moneda_list

from .usuario_views import (

    usuario_create,

    usuario_create_help,

    usuario_deactivate,

    usuario_edit,

    usuario_edit_help,

    usuario_list,

    usuario_password,

    usuario_seguridad,

)



__all__ = [

    "moneda_list",

    "moneda_create",

    "moneda_edit",

    "moneda_delete",

    "usuario_list",

    "usuario_create",

    "usuario_create_help",

    "usuario_edit",

    "usuario_edit_help",

    "usuario_deactivate",

    "usuario_password",

    "usuario_seguridad",

    "facturacion_list",

    "facturacion_create",

    "facturacion_create_help",

    "facturacion_edit",

    "facturacion_edit_help",

    "facturacion_accion",
    "noticia_list",
    "noticia_create",
    "noticia_edit",
    "noticia_copy",
    "noticia_deactivate",
    "mensajecontacto_list",
    "mensajecontacto_detail",
    "mensajecontacto_delete",
]

