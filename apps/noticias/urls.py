from django.urls import path

from apps.noticias import views

app_name = "noticias"

urlpatterns = [
    path("noticias/", views.noticia_feed, name="feed"),
    path("noticias/<int:pk>/", views.noticia_detail, name="detail"),
]
