from django.urls import path

from . import views

app_name = "ayuda"

urlpatterns = [
    path("ayuda/", views.ayuda_home, name="home"),
]
