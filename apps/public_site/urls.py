from django.urls import path

from apps.public_site import views

app_name = "public_site"

urlpatterns = [
    path("", views.home, name="home"),
    path("servicios/", views.servicios, name="servicios"),
    path("contacto/", views.contacto, name="contacto"),
]
