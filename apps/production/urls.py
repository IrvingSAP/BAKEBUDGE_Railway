from django.urls import path

from apps.production import views

app_name = "production"

urlpatterns = [
    path("produccion/", views.orden_list, name="orden_list"),
    path("produccion/nueva/ayuda/", views.orden_create_help, name="orden_create_help"),
    path("produccion/nueva/", views.orden_create, name="orden_create"),
    path(
        "produccion/<int:pk>/editar/ayuda/",
        views.orden_edit_help,
        name="orden_edit_help",
    ),
    path("produccion/<int:pk>/editar/", views.orden_edit, name="orden_edit"),
    path("produccion/<int:pk>/", views.orden_detail, name="orden_detail"),
]
