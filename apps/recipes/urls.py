from django.urls import path

from apps.recipes import views

app_name = "recipes"

urlpatterns = [
    path("recetas/", views.receta_list, name="receta_list"),
    path("recetas/nuevo/ayuda/", views.receta_create_help, name="receta_create_help"),
    path("recetas/nuevo/", views.receta_create, name="receta_create"),
    path(
        "recetas/<int:pk>/editar/ayuda/",
        views.receta_edit_help,
        name="receta_edit_help",
    ),
    path("recetas/<int:pk>/editar/", views.receta_edit, name="receta_edit"),
    path("recetas/<int:pk>/costos/", views.receta_costos, name="receta_costos"),
    path("recetas/<int:pk>/eliminar/", views.receta_delete, name="receta_delete"),
    path(
        "recetas/<int:pk>/version/ayuda/",
        views.recetaversion_edit_help,
        name="recetaversion_edit_help",
    ),
    path(
        "recetas/<int:pk>/version/",
        views.recetaversion_edit,
        name="recetaversion_edit",
    ),
    path(
        "recetas/<int:pk>/version/nueva/ayuda/",
        views.recetaversion_create_help,
        name="recetaversion_create_help",
    ),
    path(
        "recetas/<int:pk>/version/nueva/",
        views.recetaversion_create,
        name="recetaversion_create",
    ),
    path(
        "recetas/<int:pk>/versiones/",
        views.recetaversion_list,
        name="recetaversion_list",
    ),
    path(
        "recetas/<int:pk>/versiones/<int:numero>/",
        views.recetaversion_detail,
        name="recetaversion_detail",
    ),
]
