from django.shortcuts import get_object_or_404, render

from apps.recipes.decorators import recipes_access
from apps.recipes.models import Receta


@recipes_access
def receta_create_help(request):
    return render(request, "recipes/recetas/receta_create_help.html")


@recipes_access
def receta_edit_help(request, pk):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    return render(request, "recipes/recetas/receta_edit_help.html", {"receta": receta})


@recipes_access
def recetaversion_edit_help(request, pk):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    return render(request, "recipes/version/recetaversion_edit_help.html", {"receta": receta})


@recipes_access
def recetaversion_create_help(request, pk):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    return render(request, "recipes/version/recetaversion_create_help.html", {"receta": receta})
