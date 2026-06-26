from django.urls import path

from apps.catalog import views

app_name = "catalog"

urlpatterns = [
    path("productos/", views.producto_list, name="producto_list"),
    path("productos/nuevo/ayuda/", views.producto_create_help, name="producto_create_help"),
    path("productos/nuevo/", views.producto_create, name="producto_create"),
    path(
        "productos/<int:pk>/editar/ayuda/",
        views.producto_edit_help,
        name="producto_edit_help",
    ),
    path("productos/<int:pk>/editar/", views.producto_edit, name="producto_edit"),
    path("productos/<int:pk>/eliminar/", views.producto_delete, name="producto_delete"),
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nuevo/ayuda/", views.categoria_create_help, name="categoria_create_help"),
    path("categorias/nuevo/", views.categoria_create, name="categoria_create"),
    path(
        "categorias/<int:pk>/editar/ayuda/",
        views.categoria_edit_help,
        name="categoria_edit_help",
    ),
    path("categorias/<int:pk>/editar/", views.categoria_edit, name="categoria_edit"),
    path("categorias/<int:pk>/eliminar/", views.categoria_delete, name="categoria_delete"),
    path("conversiones/", views.conversion_list, name="conversion_list"),
    path(
        "conversiones/nuevo/ayuda/",
        views.conversion_create_help,
        name="conversion_create_help",
    ),
    path("conversiones/nuevo/", views.conversion_create, name="conversion_create"),
    path(
        "conversiones/<int:pk>/editar/ayuda/",
        views.conversion_edit_help,
        name="conversion_edit_help",
    ),
    path("conversiones/<int:pk>/editar/", views.conversion_edit, name="conversion_edit"),
    path("conversiones/<int:pk>/eliminar/", views.conversion_delete, name="conversion_delete"),
    path("costos-indirectos/", views.costoindirecto_list, name="costoindirecto_list"),
    path(
        "costos-indirectos/nuevo/ayuda/",
        views.costoindirecto_create_help,
        name="costoindirecto_create_help",
    ),
    path("costos-indirectos/nuevo/", views.costoindirecto_create, name="costoindirecto_create"),
    path(
        "costos-indirectos/<int:pk>/editar/ayuda/",
        views.costoindirecto_edit_help,
        name="costoindirecto_edit_help",
    ),
    path(
        "costos-indirectos/<int:pk>/editar/",
        views.costoindirecto_edit,
        name="costoindirecto_edit",
    ),
    path(
        "costos-indirectos/<int:pk>/eliminar/",
        views.costoindirecto_delete,
        name="costoindirecto_delete",
    ),
]
