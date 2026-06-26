from django.urls import path



from apps.administration import views



app_name = "administration"



urlpatterns = [

    path("administracion/monedas/", views.moneda_list, name="moneda_list"),

    path("administracion/monedas/nuevo/", views.moneda_create, name="moneda_create"),

    path(

        "administracion/monedas/<str:codigo>/editar/",

        views.moneda_edit,

        name="moneda_edit",

    ),

    path(

        "administracion/monedas/<str:codigo>/eliminar/",

        views.moneda_delete,

        name="moneda_delete",

    ),

    path("administracion/usuarios/", views.usuario_list, name="usuario_list"),

    path("administracion/usuarios/nuevo/", views.usuario_create, name="usuario_create"),

    path(

        "administracion/usuarios/nuevo/ayuda/",

        views.usuario_create_help,

        name="usuario_create_help",

    ),

    path(

        "administracion/usuarios/<int:pk>/editar/",

        views.usuario_edit,

        name="usuario_edit",

    ),

    path(

        "administracion/usuarios/<int:pk>/editar/ayuda/",

        views.usuario_edit_help,

        name="usuario_edit_help",

    ),

    path(

        "administracion/usuarios/<int:pk>/desactivar/",

        views.usuario_deactivate,

        name="usuario_deactivate",

    ),

    path(

        "administracion/usuarios/<int:pk>/contrasena/",

        views.usuario_password,

        name="usuario_password",

    ),

    path(

        "administracion/usuarios/<int:pk>/seguridad/",

        views.usuario_seguridad,

        name="usuario_seguridad",

    ),

    path("administracion/facturacion/", views.facturacion_list, name="facturacion_list"),

    path(

        "administracion/facturacion/nuevo/",

        views.facturacion_create,

        name="facturacion_create",

    ),

    path(

        "administracion/facturacion/nuevo/ayuda/",

        views.facturacion_create_help,

        name="facturacion_create_help",

    ),

    path(

        "administracion/facturacion/<int:pk>/editar/",

        views.facturacion_edit,

        name="facturacion_edit",

    ),

    path(

        "administracion/facturacion/<int:pk>/editar/ayuda/",

        views.facturacion_edit_help,

        name="facturacion_edit_help",

    ),

    path(
        "administracion/facturacion/<int:pk>/accion/",
        views.facturacion_accion,
        name="facturacion_accion",
    ),
    path("administracion/noticias/", views.noticia_list, name="noticia_list"),
    path("administracion/noticias/nuevo/", views.noticia_create, name="noticia_create"),
    path(
        "administracion/noticias/<int:pk>/editar/",
        views.noticia_edit,
        name="noticia_edit",
    ),
    path(
        "administracion/noticias/<int:pk>/copiar/",
        views.noticia_copy,
        name="noticia_copy",
    ),
    path(
        "administracion/noticias/<int:pk>/desactivar/",
        views.noticia_deactivate,
        name="noticia_deactivate",
    ),
    path(
        "administracion/mensajes-contacto/",
        views.mensajecontacto_list,
        name="mensajecontacto_list",
    ),
    path(
        "administracion/mensajes-contacto/<int:pk>/",
        views.mensajecontacto_detail,
        name="mensajecontacto_detail",
    ),
    path(
        "administracion/mensajes-contacto/<int:pk>/eliminar/",
        views.mensajecontacto_delete,
        name="mensajecontacto_delete",
    ),
]

