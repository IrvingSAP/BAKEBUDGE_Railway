from django.urls import path

from apps.analytics import views

app_name = "analytics"

urlpatterns = [
    path("estadisticas/", views.estadisticas_home, name="estadisticas_home"),
]
