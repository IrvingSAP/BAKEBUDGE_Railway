from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("perfil/", views.perfil, name="perfil"),
    path("seguridad/cuenta/", views.cuenta_seguridad, name="cuenta_seguridad"),
]
