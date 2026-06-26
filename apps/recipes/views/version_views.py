from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.form_validation import form_error_context
from apps.recipes.decorators import recipes_access
from apps.recipes.models import Receta, RecetaVersion
from apps.recipes.services.version_helpers import (
    crear_nueva_version,
    formulacion_context,
    guardar_formulacion,
    indirectos_filas_from_post,
    ingredientes_filas_from_post,
    parse_formulacion_post,
)


def _version_form_data(version):
    return {
        "rendimiento_cantidad": str(version.rendimiento_cantidad),
        "rendimiento_unidad": version.rendimiento_unidad,
        "precio_venta_sugerido": str(version.precio_venta_sugerido),
        "precio_override_manual": False,
    }


@recipes_access
def recetaversion_edit(request, pk):
    receta = get_object_or_404(
        Receta.objects.select_related("version_actual"),
        pk=pk,
        owner=request.user,
    )
    version = receta.version_actual
    if version is None:
        messages.error(request, "La receta no tiene versión vigente.")
        return redirect("recipes:receta_edit", pk=receta.pk)

    form_data = _version_form_data(version)

    if request.method == "POST":
        form_data = parse_formulacion_post(request.POST)
        errors = {}
        if guardar_formulacion(version, request.user, form_data, errors):
            messages.success(request, "Formulación guardada correctamente.")
            return redirect("recipes:recetaversion_edit", pk=receta.pk)

        context = {
            "receta": receta,
            "version": version,
            "form_data": form_data,
            **formulacion_context(version, request.user),
            "ingredientes_filas": ingredientes_filas_from_post(form_data),
            "indirectos_filas": indirectos_filas_from_post(form_data),
        }
        context.update(form_error_context(errors))
        return render(request, "recipes/version/recetaversion_edit.html", context)

    extra = formulacion_context(version, request.user)
    return render(
        request,
        "recipes/version/recetaversion_edit.html",
        {
            "receta": receta,
            "version": version,
            "form_data": form_data,
            **extra,
        },
    )


@recipes_access
def recetaversion_create(request, pk):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    notas_cambio = ""

    if request.method == "POST":
        notas_cambio = request.POST.get("notas_cambio", "").strip()
        if not notas_cambio:
            messages.error(request, "Indica el motivo del cambio de versión.")
            return render(
                request,
                "recipes/version/recetaversion_create.html",
                {"receta": receta, "notas_cambio": notas_cambio},
            )
        crear_nueva_version(receta, notas_cambio=notas_cambio)
        messages.success(request, f"Versión {receta.version_actual.etiqueta} creada.")
        return redirect("recipes:recetaversion_edit", pk=receta.pk)

    return render(
        request,
        "recipes/version/recetaversion_create.html",
        {"receta": receta, "notas_cambio": notas_cambio},
    )


@recipes_access
def recetaversion_list(request, pk):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    versiones = receta.versiones.order_by("-numero_version")
    return render(
        request,
        "recipes/version/recetaversion_list.html",
        {"receta": receta, "versiones": versiones},
    )


@recipes_access
def recetaversion_detail(request, pk, numero):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    version = get_object_or_404(RecetaVersion, receta=receta, numero_version=numero)
    extra = formulacion_context(version, request.user)
    return render(
        request,
        "recipes/version/recetaversion_detail.html",
        {"receta": receta, "version": version, **extra, "readonly": True},
    )
