from django.shortcuts import get_object_or_404, render

from apps.catalog.decorators import catalog_access
from apps.catalog.models import CostoIndirecto, ConversionUnidad, ProductCategory, Producto


@catalog_access
def producto_create_help(request):
    return render(request, "catalog/productos/producto_create_help.html")


@catalog_access
def producto_edit_help(request, pk):
    producto = get_object_or_404(Producto, pk=pk, owner=request.user)
    return render(
        request,
        "catalog/productos/producto_edit_help.html",
        {"producto": producto},
    )


@catalog_access
def categoria_create_help(request):
    return render(request, "catalog/categorias/categoria_create_help.html")


@catalog_access
def categoria_edit_help(request, pk):
    categoria = get_object_or_404(ProductCategory, pk=pk, owner=request.user)
    return render(
        request,
        "catalog/categorias/categoria_edit_help.html",
        {"categoria": categoria},
    )


@catalog_access
def conversion_create_help(request):
    return render(request, "catalog/conversiones/conversion_create_help.html")


@catalog_access
def conversion_edit_help(request, pk):
    conversion = get_object_or_404(ConversionUnidad, pk=pk, owner=request.user)
    return render(
        request,
        "catalog/conversiones/conversion_edit_help.html",
        {"conversion": conversion},
    )


@catalog_access
def costoindirecto_create_help(request):
    return render(request, "catalog/costos_indirectos/costoindirecto_create_help.html")


@catalog_access
def costoindirecto_edit_help(request, pk):
    costo_indirecto = get_object_or_404(CostoIndirecto, pk=pk, owner=request.user)
    return render(
        request,
        "catalog/costos_indirectos/costoindirecto_edit_help.html",
        {"costo_indirecto": costo_indirecto},
    )
