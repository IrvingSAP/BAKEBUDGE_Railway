from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.form_validation import form_error_context
from apps.recipes.constants import Status
from apps.recipes.decorators import recipes_access
from apps.recipes.models import Receta
from apps.recipes.services.receta_helpers import (
    crear_receta_con_version_inicial,
    parse_receta_create_post,
    parse_receta_edit_post,
    validate_receta_create,
    validate_receta_edit,
)
from apps.recipes.services.cost_calculator import (
    list_indirectos_costo_detalle,
    list_ingredientes_costo_detalle,
)


def _status_choices():
    return Status.choices


def _receta_form_defaults():
    return {
        "nombre": "",
        "descripcion_corta": "",
        "notas": "",
        "rendimiento_cantidad": "1",
        "rendimiento_unidad": "porciones",
        "status": Status.EN_PROCESO,
    }


@recipes_access
def receta_list(request):
    recetas = (
        Receta.objects.filter(owner=request.user)
        .select_related("version_actual")
        .order_by("nombre")
    )
    return render(request, "recipes/recetas/receta_list.html", {"recetas": recetas})


@recipes_access
def receta_create(request):
    form_data = _receta_form_defaults()
    if request.method == "POST":
        form_data = parse_receta_create_post(request.POST, request.FILES)
        errors = {}
        rendimiento = validate_receta_create(form_data, errors)
        if errors:
            context = {"form_data": form_data, "status_choices": _status_choices()}
            context.update(form_error_context(errors))
            return render(request, "recipes/recetas/receta_form.html", context)

        crear_receta_con_version_inicial(request.user, form_data, rendimiento)
        messages.success(request, "Receta creada correctamente con versión v1.")
        return redirect("recipes:receta_list")

    return render(
        request,
        "recipes/recetas/receta_form.html",
        {"form_data": form_data, "status_choices": _status_choices()},
    )


@recipes_access
def receta_edit(request, pk):
    receta = get_object_or_404(
        Receta.objects.select_related("version_actual"),
        pk=pk,
        owner=request.user,
    )
    version = receta.version_actual
    form_data = {
        "nombre": receta.nombre,
        "descripcion_corta": receta.descripcion_corta,
        "notas": receta.notas,
        "status": receta.status,
    }

    if request.method == "POST":
        form_data = parse_receta_edit_post(request.POST, request.FILES)
        errors = {}
        validate_receta_edit(form_data, errors)
        if errors:
            context = {
                "form_data": form_data,
                "receta": receta,
                "version": version,
                "status_choices": _status_choices(),
            }
            context.update(form_error_context(errors))
            return render(request, "recipes/recetas/receta_form.html", context)

        receta.nombre = form_data["nombre"]
        receta.descripcion_corta = form_data.get("descripcion_corta", "")
        receta.notas = form_data.get("notas", "")
        receta.status = form_data["status"]
        if form_data.get("imagen"):
            receta.imagen = form_data["imagen"]
        receta.save()
        messages.success(request, "Receta actualizada correctamente.")
        return redirect("recipes:receta_list")

    return render(
        request,
        "recipes/recetas/receta_form.html",
        {
            "form_data": form_data,
            "receta": receta,
            "version": version,
            "status_choices": _status_choices(),
        },
    )


@recipes_access
def receta_delete(request, pk):
    receta = get_object_or_404(Receta, pk=pk, owner=request.user)
    if request.method == "POST":
        accion = request.POST.get("accion", "inactivar")
        if accion == "eliminar":
            receta.delete()
            messages.success(request, "Receta eliminada permanentemente.")
        else:
            receta.status = Status.INACTIVO
            receta.save(update_fields=["status", "updated_at"])
            messages.success(request, "Receta marcada como inactiva.")
        return redirect("recipes:receta_list")

    return render(request, "recipes/recetas/receta_delete.html", {"receta": receta})


@recipes_access
def receta_costos(request, pk):
    receta = get_object_or_404(
        Receta.objects.select_related("version_actual"),
        pk=pk,
        owner=request.user,
    )
    version = receta.version_actual
    if version is None:
        messages.error(request, "La receta no tiene versión vigente con costos.")
        return redirect("recipes:receta_list")

    return render(
        request,
        "recipes/recetas/receta_costos.html",
        {
            "receta": receta,
            "version": version,
            "lineas_costo": list_ingredientes_costo_detalle(version),
            "lineas_indirecto": list_indirectos_costo_detalle(version),
        },
    )
