from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.form_validation import form_error_context
from apps.production.decorators import production_access
from apps.production.constants import Estado
from apps.production.models import OrdenProduccion
from apps.production.services.detail_helpers import orden_detalle_context
from apps.production.services.order_helpers import (
    actualizar_orden_borrador,
    avisos_receta,
    crear_orden,
    parse_orden_create_post,
    parse_orden_edit_post,
    recetas_para_planificacion,
    recetas_preview_data,
    validate_orden_create,
    validate_orden_edit,
)
from apps.production.services.state_transitions import (
    cancelar_orden,
    completar_orden,
    iniciar_produccion,
)


def _parse_fecha(raw):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


def _orden_form_defaults(receta_id=""):
    return {
        "receta_id": receta_id,
        "cantidad_lotes": "1",
        "fecha_programada": "",
        "notas": "",
    }


@production_access
def orden_list(request):
    ordenes = (
        OrdenProduccion.objects.filter(owner=request.user)
        .select_related("receta_version__receta")
        .order_by("-fecha_programada", "-created_at")
    )
    return render(request, "production/orden_list.html", {"ordenes": ordenes})


@production_access
def orden_create(request):
    receta_id_pre = request.GET.get("receta_id", "").strip()
    form_data = _orden_form_defaults(receta_id_pre)
    recetas = recetas_para_planificacion(request.user)
    preview_data = recetas_preview_data(request.user)

    if request.method == "POST":
        form_data = parse_orden_create_post(request.POST)
        errors = {}
        receta, version, lotes = validate_orden_create(request.user, form_data, errors)
        if errors:
            context = {
                "form_data": form_data,
                "recetas": recetas,
                "recetas_preview": preview_data,
                "avisos": avisos_receta(receta, version) if receta and version else [],
            }
            context.update(form_error_context(errors))
            return render(request, "production/orden_create.html", context)

        fecha = _parse_fecha(form_data["fecha_programada"])
        if form_data["fecha_programada"] and fecha is None:
            errors["fecha_programada"] = "Fecha no válida."
            context = {
                "form_data": form_data,
                "recetas": recetas,
                "recetas_preview": preview_data,
                "avisos": avisos_receta(receta, version),
            }
            context.update(form_error_context(errors))
            return render(request, "production/orden_create.html", context)

        orden = crear_orden(
            request.user,
            receta,
            version,
            lotes,
            fecha_programada=fecha,
            notas=form_data["notas"],
        )
        messages.success(request, f"Orden {orden.codigo} creada en borrador.")
        return redirect("production:orden_detail", pk=orden.pk)

    avisos = []
    if receta_id_pre:
        from apps.production.services.order_helpers import get_receta_for_order

        receta = get_receta_for_order(request.user, receta_id_pre)
        if receta and receta.version_actual:
            avisos = avisos_receta(receta, receta.version_actual)

    return render(
        request,
        "production/orden_create.html",
        {
            "form_data": form_data,
            "recetas": recetas,
            "recetas_preview": preview_data,
            "avisos": avisos,
        },
    )


@production_access
def orden_edit(request, pk):
    orden = get_object_or_404(
        OrdenProduccion.objects.select_related("receta_version__receta"),
        pk=pk,
        owner=request.user,
    )
    if not orden.es_editable:
        messages.error(request, "Solo se editan órdenes en borrador.")
        return redirect("production:orden_detail", pk=orden.pk)

    form_data = {
        "cantidad_lotes": str(orden.cantidad_lotes),
        "fecha_programada": (
            orden.fecha_programada.isoformat() if orden.fecha_programada else ""
        ),
        "notas": orden.notas,
    }

    if request.method == "POST":
        form_data = parse_orden_edit_post(request.POST)
        errors = {}
        lotes = validate_orden_edit(form_data, errors)
        if errors:
            context = {"orden": orden, "form_data": form_data}
            context.update(form_error_context(errors))
            return render(request, "production/orden_edit.html", context)

        fecha = _parse_fecha(form_data["fecha_programada"])
        if form_data["fecha_programada"] and fecha is None:
            errors["fecha_programada"] = "Fecha no válida."
            context = {"orden": orden, "form_data": form_data}
            context.update(form_error_context(errors))
            return render(request, "production/orden_edit.html", context)

        actualizar_orden_borrador(
            orden,
            lotes,
            fecha_programada=fecha,
            notas=form_data["notas"],
        )
        messages.success(request, "Orden actualizada.")
        return redirect("production:orden_detail", pk=orden.pk)

    return render(
        request,
        "production/orden_edit.html",
        {"orden": orden, "form_data": form_data},
    )


@production_access
def orden_detail(request, pk):
    orden = get_object_or_404(
        OrdenProduccion.objects.select_related("receta_version__receta", "analytics"),
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        errors = {}
        ok = False

        if action == "iniciar":
            ok = iniciar_produccion(orden, errors)
            if ok:
                messages.success(request, "Producción iniciada. Costo estimado congelado.")
        elif action == "cancelar":
            ok = cancelar_orden(orden, errors)
            if ok:
                messages.success(request, "Orden cancelada.")
        elif action == "completar":
            ok = completar_orden(orden, request.POST, errors)
            if ok:
                messages.success(request, "Orden completada.")
        else:
            errors["action"] = "Acción no válida."

        if errors:
            context = {
                "orden": orden,
                "tiene_analytics": hasattr(orden, "analytics"),
                "precio_form": {
                    "precio_venta_unitario": request.POST.get("precio_venta_unitario", ""),
                    "precio_venta_total": request.POST.get("precio_venta_total", ""),
                },
                **orden_detalle_context(orden),
            }
            context.update(form_error_context(errors))
            return render(request, "production/orden_detail.html", context)

        return redirect("production:orden_detail", pk=orden.pk)

    precio_default = orden.receta_version.precio_venta_sugerido
    precio_form = {
        "precio_venta_unitario": (
            str(orden.precio_venta_unitario)
            if orden.precio_venta_unitario is not None
            else str(precio_default)
        ),
        "precio_venta_total": (
            str(orden.precio_venta_total) if orden.precio_venta_total is not None else ""
        ),
    }

    return render(
        request,
        "production/orden_detail.html",
        {
            "orden": orden,
            "tiene_analytics": hasattr(orden, "analytics"),
            "precio_form": precio_form,
            "precio_sugerido": precio_default,
            **orden_detalle_context(orden),
        },
    )
