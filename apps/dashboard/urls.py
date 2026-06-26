from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("acceso-denegado/", views.access_denied, name="access_denied"),
]
