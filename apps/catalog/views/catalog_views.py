from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.catalog.constants import Status, UnidadCobro
from apps.catalog.decorators import catalog_access
from apps.catalog.models import CostoIndirecto, ConversionUnidad, ProductCategory, Producto
from apps.core.form_validation import form_error_context, parse_decimal as _parse_decimal


STATUS_VALUES = {value for value, _ in Status.choices}
UNIDAD_COBRO_VALUES = {value for value, _ in UnidadCobro.choices}


def _parse_bool(value):
    return value in {"1", "true", "on", "si", "sí"}


def _status_choices():
    return Status.choices


def _unidad_cobro_choices():
    return UnidadCobro.choices


def _producto_form_context(request, form_data, producto=None):
    categorias = ProductCategory.objects.filter(owner=request.user).order_by("orden", "nombre")
    unidades = list(
        ConversionUnidad.objects.filter(owner=request.user)
        .values_list("hacia_unidad", flat=True)
        .distinct()
        .order_by("hacia_unidad")
    )
    if producto and producto.unidad_base not in unidades:
        unidades.append(producto.unidad_base)
        unidades.sort()
    return {
        "form_data": form_data,
        "categorias": categorias,
        "unidad_base_options": unidades,
        "status_choices": _status_choices(),
        "producto": producto,
    }


@catalog_access
def producto_list(request):
    productos = (
        Producto.objects.filter(owner=request.user)
        .select_related("categoria")
        .order_by("nombre")
    )
    categorias = (
        ProductCategory.objects.filter(owner=request.user)
        .order_by("orden", "nombre")
        .values_list("nombre", flat=True)
    )
    return render(
        request,
        "catalog/productos/producto_list.html",
        {"productos": productos, "categorias": categorias},
    )


@catalog_access
def producto_create(request):
    form_data = {
        "nombre": "",
        "categoria": "",
        "unidad_base": "",
        "costo_por_unidad_base": "",
        "status": Status.EN_PROCESO,
        "proveedor": "",
        "notas": "",
    }
    context = _producto_form_context(request, form_data)
    if not context["unidad_base_options"]:
        link = reverse("catalog:conversion_list")
        messages.error(
            request,
            mark_safe(
                "Primero debes crear al menos una conversión de unidad para definir la unidad base. "
                f'<a href="{link}">Ir a conversiones</a>.'
            ),
        )
        return redirect("catalog:conversion_list")

    if request.method == "POST":
        form_data = {
            "nombre": request.POST.get("nombre", "").strip(),
            "categoria": request.POST.get("categoria", "").strip(),
            "unidad_base": request.POST.get("unidad_base", "").strip(),
            "costo_por_unidad_base": request.POST.get("costo_por_unidad_base", "").strip(),
            "status": request.POST.get("status", Status.EN_PROCESO).strip(),
            "proveedor": request.POST.get("proveedor", "").strip(),
            "notas": request.POST.get("notas", "").strip(),
        }
        errors = {}
        categoria = None

        if not form_data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        if form_data["status"] not in STATUS_VALUES:
            errors["status"] = "Selecciona un estado válido."

        if not form_data["categoria"]:
            errors["categoria"] = "Selecciona una categoría."
        else:
            categoria = ProductCategory.objects.filter(
                owner=request.user,
                pk=form_data["categoria"],
                status=Status.ACTIVO,
            ).first()
            if categoria is None:
                errors["categoria"] = "La categoría debe ser activa y pertenecer a tu catálogo."

        if form_data["unidad_base"] not in context["unidad_base_options"]:
            errors["unidad_base"] = "Selecciona una unidad base válida desde tus conversiones."

        costo = _parse_decimal(form_data["costo_por_unidad_base"], "costo_por_unidad_base", errors)
        if costo is not None and costo <= 0:
            errors["costo_por_unidad_base"] = "El costo por unidad base debe ser mayor que 0."

        if errors:
            context = _producto_form_context(request, form_data)
            context.update(form_error_context(errors))
            return render(request, "catalog/productos/producto_form.html", context)

        Producto.objects.create(
            owner=request.user,
            nombre=form_data["nombre"],
            categoria=categoria,
            unidad_base=form_data["unidad_base"],
            costo_por_unidad_base=costo,
            status=form_data["status"],
            proveedor=form_data["proveedor"],
            notas=form_data["notas"],
        )
        messages.success(request, "Producto creado correctamente.")
        return redirect("catalog:producto_list")

    return render(request, "catalog/productos/producto_form.html", context)


@catalog_access
def producto_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk, owner=request.user)
    form_data = {
        "nombre": producto.nombre,
        "categoria": str(producto.categoria_id),
        "unidad_base": producto.unidad_base,
        "costo_por_unidad_base": str(producto.costo_por_unidad_base),
        "status": producto.status,
        "proveedor": producto.proveedor,
        "notas": producto.notas,
    }

    if request.method == "POST":
        form_data = {
            "nombre": request.POST.get("nombre", "").strip(),
            "categoria": request.POST.get("categoria", "").strip(),
            "unidad_base": request.POST.get("unidad_base", "").strip(),
            "costo_por_unidad_base": request.POST.get("costo_por_unidad_base", "").strip(),
            "status": request.POST.get("status", Status.EN_PROCESO).strip(),
            "proveedor": request.POST.get("proveedor", "").strip(),
            "notas": request.POST.get("notas", "").strip(),
        }
        errors = {}
        categoria = None
        context = _producto_form_context(request, form_data, producto=producto)

        if not form_data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        if form_data["status"] not in STATUS_VALUES:
            errors["status"] = "Selecciona un estado válido."

        if not form_data["categoria"]:
            errors["categoria"] = "Selecciona una categoría."
        else:
            categoria = ProductCategory.objects.filter(owner=request.user, pk=form_data["categoria"]).first()
            if categoria is None:
                errors["categoria"] = "La categoría debe pertenecer a tu catálogo."

        if form_data["unidad_base"] not in context["unidad_base_options"]:
            errors["unidad_base"] = "Selecciona una unidad base válida desde tus conversiones."

        costo = _parse_decimal(form_data["costo_por_unidad_base"], "costo_por_unidad_base", errors)
        if costo is not None and costo <= 0:
            errors["costo_por_unidad_base"] = "El costo por unidad base debe ser mayor que 0."

        if errors:
            context.update(form_error_context(errors))
            return render(request, "catalog/productos/producto_form.html", context)

        producto.nombre = form_data["nombre"]
        producto.categoria = categoria
        producto.unidad_base = form_data["unidad_base"]
        producto.costo_por_unidad_base = costo
        producto.status = form_data["status"]
        producto.proveedor = form_data["proveedor"]
        producto.notas = form_data["notas"]
        producto.full_clean()
        producto.save()
        messages.success(request, "Producto actualizado correctamente.")
        return redirect("catalog:producto_list")

    context = _producto_form_context(request, form_data, producto=producto)
    return render(request, "catalog/productos/producto_form.html", context)


@catalog_access
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk, owner=request.user)
    if request.method == "POST":
        try:
            producto.delete()
            messages.success(request, "Producto eliminado correctamente.")
        except ProtectedError:
            producto.status = Status.INACTIVO
            producto.save(update_fields=["status", "updated_at"])
            messages.success(
                request,
                "El producto no pudo eliminarse físicamente y quedó inactivo.",
            )
        return redirect("catalog:producto_list")

    return render(request, "catalog/productos/producto_delete.html", {"producto": producto})


@catalog_access
def categoria_list(request):
    categorias = ProductCategory.objects.filter(owner=request.user).order_by("orden", "nombre")
    return render(request, "catalog/categorias/categoria_list.html", {"categorias": categorias})


@catalog_access
def categoria_create(request):
    form_data = {
        "nombre": "",
        "codigo": "",
        "descripcion": "",
        "orden": "0",
        "color": "",
        "status": Status.ACTIVO,
        "es_predeterminada": False,
    }
    if request.method == "POST":
        form_data = {
            "nombre": request.POST.get("nombre", "").strip(),
            "codigo": request.POST.get("codigo", "").strip(),
            "descripcion": request.POST.get("descripcion", "").strip(),
            "orden": request.POST.get("orden", "0").strip(),
            "color": request.POST.get("color", "").strip(),
            "status": request.POST.get("status", Status.ACTIVO).strip(),
            "es_predeterminada": _parse_bool(request.POST.get("es_predeterminada", "")),
        }
        errors = {}
        if not form_data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        if form_data["status"] not in STATUS_VALUES:
            errors["status"] = "Selecciona un estado válido."
        try:
            orden = int(form_data["orden"] or "0")
            if orden < 0:
                raise ValueError
        except ValueError:
            orden = 0
            errors["orden"] = "El orden debe ser un número entero mayor o igual a 0."

        if errors:
            return render(
                request,
                "catalog/categorias/categoria_form.html",
                {
                    "form_data": form_data,
                    "status_choices": _status_choices(),
                    **form_error_context(errors),
                },
            )

        ProductCategory.objects.create(
            owner=request.user,
            nombre=form_data["nombre"],
            codigo=form_data["codigo"],
            descripcion=form_data["descripcion"],
            orden=orden,
            color=form_data["color"],
            status=form_data["status"],
            es_predeterminada=form_data["es_predeterminada"],
        )
        messages.success(request, "Categoría creada correctamente.")
        return redirect("catalog:categoria_list")

    return render(
        request,
        "catalog/categorias/categoria_form.html",
        {"form_data": form_data, "status_choices": _status_choices()},
    )


@catalog_access
def categoria_edit(request, pk):
    categoria = get_object_or_404(ProductCategory, pk=pk, owner=request.user)
    form_data = {
        "nombre": categoria.nombre,
        "codigo": categoria.codigo,
        "descripcion": categoria.descripcion,
        "orden": str(categoria.orden),
        "color": categoria.color,
        "status": categoria.status,
        "es_predeterminada": categoria.es_predeterminada,
    }
    if request.method == "POST":
        form_data = {
            "nombre": request.POST.get("nombre", "").strip(),
            "codigo": request.POST.get("codigo", "").strip(),
            "descripcion": request.POST.get("descripcion", "").strip(),
            "orden": request.POST.get("orden", "0").strip(),
            "color": request.POST.get("color", "").strip(),
            "status": request.POST.get("status", Status.ACTIVO).strip(),
            "es_predeterminada": _parse_bool(request.POST.get("es_predeterminada", "")),
        }
        errors = {}
        if not form_data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        if form_data["status"] not in STATUS_VALUES:
            errors["status"] = "Selecciona un estado válido."
        try:
            orden = int(form_data["orden"] or "0")
            if orden < 0:
                raise ValueError
        except ValueError:
            orden = 0
            errors["orden"] = "El orden debe ser un número entero mayor o igual a 0."

        if errors:
            return render(
                request,
                "catalog/categorias/categoria_form.html",
                {
                    "form_data": form_data,
                    "status_choices": _status_choices(),
                    "categoria": categoria,
                    **form_error_context(errors),
                },
            )

        categoria.nombre = form_data["nombre"]
        categoria.codigo = form_data["codigo"]
        categoria.descripcion = form_data["descripcion"]
        categoria.orden = orden
        categoria.color = form_data["color"]
        categoria.status = form_data["status"]
        categoria.es_predeterminada = form_data["es_predeterminada"]
        categoria.full_clean()
        categoria.save()
        messages.success(request, "Categoría actualizada correctamente.")
        return redirect("catalog:categoria_list")

    return render(
        request,
        "catalog/categorias/categoria_form.html",
        {"form_data": form_data, "status_choices": _status_choices(), "categoria": categoria},
    )


@catalog_access
def categoria_delete(request, pk):
    categoria = get_object_or_404(ProductCategory, pk=pk, owner=request.user)
    productos_count = categoria.productos.count()
    if request.method == "POST":
        if productos_count > 0 and categoria.es_predeterminada:
            messages.error(
                request,
                "No puedes eliminar una categoría predeterminada que tiene productos asociados.",
            )
            return redirect("catalog:categoria_list")
        if productos_count > 0:
            messages.error(
                request,
                "No puedes eliminar esta categoría porque tiene productos asociados.",
            )
            return redirect("catalog:categoria_list")

        categoria.delete()
        messages.success(request, "Categoría eliminada correctamente.")
        return redirect("catalog:categoria_list")

    return render(
        request,
        "catalog/categorias/categoria_delete.html",
        {"categoria": categoria, "productos_count": productos_count},
    )


@catalog_access
def conversion_list(request):
    conversiones = (
        ConversionUnidad.objects.filter(owner=request.user)
        .select_related("producto")
        .order_by("desde_unidad", "hacia_unidad", "nombre")
    )
    hacia_unidades = (
        ConversionUnidad.objects.filter(owner=request.user)
        .values_list("hacia_unidad", flat=True)
        .distinct()
        .order_by("hacia_unidad")
    )
    return render(
        request,
        "catalog/conversiones/conversion_list.html",
        {"conversiones": conversiones, "hacia_unidades": hacia_unidades},
    )


@catalog_access
def conversion_create(request):
    productos = Producto.objects.filter(owner=request.user).order_by("nombre")
    form_data = {
        "producto": "",
        "nombre": "",
        "desde_unidad": "",
        "hacia_unidad": "",
        "factor": "",
        "notas": "",
    }
    if request.method == "POST":
        form_data = {
            "producto": request.POST.get("producto", "").strip(),
            "nombre": request.POST.get("nombre", "").strip(),
            "desde_unidad": request.POST.get("desde_unidad", "").strip(),
            "hacia_unidad": request.POST.get("hacia_unidad", "").strip(),
            "factor": request.POST.get("factor", "").strip(),
            "notas": request.POST.get("notas", "").strip(),
        }
        errors = {}
        producto = None
        if form_data["producto"]:
            producto = Producto.objects.filter(owner=request.user, pk=form_data["producto"]).first()
            if producto is None:
                errors["producto"] = "El producto seleccionado no es válido."

        if not form_data["desde_unidad"]:
            errors["desde_unidad"] = "La unidad desde es obligatoria."
        if not form_data["hacia_unidad"]:
            errors["hacia_unidad"] = "La unidad hacia es obligatoria."

        factor = _parse_decimal(form_data["factor"], "factor", errors)
        if factor is not None and factor <= 0:
            errors["factor"] = "El factor debe ser mayor que 0."

        if producto and form_data["hacia_unidad"] != producto.unidad_base:
            errors["hacia_unidad"] = "Debe coincidir con la unidad base del producto seleccionado."

        if errors:
            return render(
                request,
                "catalog/conversiones/conversion_form.html",
                {
                    "form_data": form_data,
                    "productos": productos,
                    **form_error_context(errors),
                },
            )

        ConversionUnidad.objects.create(
            owner=request.user,
            producto=producto,
            nombre=form_data["nombre"],
            desde_unidad=form_data["desde_unidad"],
            hacia_unidad=form_data["hacia_unidad"],
            factor=factor,
            notas=form_data["notas"],
        )
        messages.success(request, "Conversión creada correctamente.")
        return redirect("catalog:conversion_list")

    return render(
        request,
        "catalog/conversiones/conversion_form.html",
        {"form_data": form_data, "productos": productos},
    )


@catalog_access
def conversion_edit(request, pk):
    conversion = get_object_or_404(
        ConversionUnidad.objects.select_related("producto"),
        pk=pk,
        owner=request.user,
    )
    productos = Producto.objects.filter(owner=request.user).order_by("nombre")
    form_data = {
        "producto": str(conversion.producto_id or ""),
        "nombre": conversion.nombre,
        "desde_unidad": conversion.desde_unidad,
        "hacia_unidad": conversion.hacia_unidad,
        "factor": str(conversion.factor),
        "notas": conversion.notas,
    }
    if request.method == "POST":
        form_data = {
            "producto": request.POST.get("producto", "").strip(),
            "nombre": request.POST.get("nombre", "").strip(),
            "desde_unidad": request.POST.get("desde_unidad", "").strip(),
            "hacia_unidad": request.POST.get("hacia_unidad", "").strip(),
            "factor": request.POST.get("factor", "").strip(),
            "notas": request.POST.get("notas", "").strip(),
        }
        errors = {}
        producto = None
        if form_data["producto"]:
            producto = Producto.objects.filter(owner=request.user, pk=form_data["producto"]).first()
            if producto is None:
                errors["producto"] = "El producto seleccionado no es válido."

        if not form_data["desde_unidad"]:
            errors["desde_unidad"] = "La unidad desde es obligatoria."
        if not form_data["hacia_unidad"]:
            errors["hacia_unidad"] = "La unidad hacia es obligatoria."

        factor = _parse_decimal(form_data["factor"], "factor", errors)
        if factor is not None and factor <= 0:
            errors["factor"] = "El factor debe ser mayor que 0."

        if producto and form_data["hacia_unidad"] != producto.unidad_base:
            errors["hacia_unidad"] = "Debe coincidir con la unidad base del producto seleccionado."

        if errors:
            return render(
                request,
                "catalog/conversiones/conversion_form.html",
                {
                    "form_data": form_data,
                    "productos": productos,
                    "conversion": conversion,
                    **form_error_context(errors),
                },
            )

        conversion.producto = producto
        conversion.nombre = form_data["nombre"]
        conversion.desde_unidad = form_data["desde_unidad"]
        conversion.hacia_unidad = form_data["hacia_unidad"]
        conversion.factor = factor
        conversion.notas = form_data["notas"]
        conversion.full_clean()
        conversion.save()
        messages.success(request, "Conversión actualizada correctamente.")
        return redirect("catalog:conversion_list")

    return render(
        request,
        "catalog/conversiones/conversion_form.html",
        {"form_data": form_data, "productos": productos, "conversion": conversion},
    )


@catalog_access
def conversion_delete(request, pk):
    conversion = get_object_or_404(ConversionUnidad, pk=pk, owner=request.user)
    if request.method == "POST":
        conversion.delete()
        messages.success(request, "Conversión eliminada correctamente.")
        return redirect("catalog:conversion_list")
    return render(request, "catalog/conversiones/conversion_delete.html", {"conversion": conversion})


@catalog_access
def costoindirecto_list(request):
    costos = CostoIndirecto.objects.filter(owner=request.user).order_by("nombre")
    return render(request, "catalog/costos_indirectos/costoindirecto_list.html", {"costos": costos})


@catalog_access
def costoindirecto_create(request):
    form_data = {
        "nombre": "",
        "unidad_cobro": UnidadCobro.HORA,
        "costo_por_unidad": "",
        "status": Status.EN_PROCESO,
        "notas": "",
    }
    if request.method == "POST":
        form_data = {
            "nombre": request.POST.get("nombre", "").strip(),
            "unidad_cobro": request.POST.get("unidad_cobro", UnidadCobro.HORA).strip(),
            "costo_por_unidad": request.POST.get("costo_por_unidad", "").strip(),
            "status": request.POST.get("status", Status.EN_PROCESO).strip(),
            "notas": request.POST.get("notas", "").strip(),
        }
        errors = {}
        if not form_data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        if form_data["unidad_cobro"] not in UNIDAD_COBRO_VALUES:
            errors["unidad_cobro"] = "Selecciona una unidad de cobro válida."
        if form_data["status"] not in STATUS_VALUES:
            errors["status"] = "Selecciona un estado válido."

        costo = _parse_decimal(form_data["costo_por_unidad"], "costo_por_unidad", errors)
        if costo is not None and costo < 0:
            errors["costo_por_unidad"] = "El costo no puede ser negativo."
        if costo is not None and form_data["status"] == Status.ACTIVO and costo <= 0:
            errors["costo_por_unidad"] = "Para estado activo el costo debe ser mayor que 0."

        if errors:
            return render(
                request,
                "catalog/costos_indirectos/costoindirecto_form.html",
                {
                    "form_data": form_data,
                    "status_choices": _status_choices(),
                    "unidad_cobro_choices": _unidad_cobro_choices(),
                    **form_error_context(errors),
                },
            )

        CostoIndirecto.objects.create(
            owner=request.user,
            nombre=form_data["nombre"],
            unidad_cobro=form_data["unidad_cobro"],
            costo_por_unidad=costo,
            status=form_data["status"],
            notas=form_data["notas"],
        )
        messages.success(request, "Costo indirecto creado correctamente.")
        return redirect("catalog:costoindirecto_list")

    return render(
        request,
        "catalog/costos_indirectos/costoindirecto_form.html",
        {
            "form_data": form_data,
            "status_choices": _status_choices(),
            "unidad_cobro_choices": _unidad_cobro_choices(),
        },
    )


@catalog_access
def costoindirecto_edit(request, pk):
    costo_indirecto = get_object_or_404(CostoIndirecto, pk=pk, owner=request.user)
    form_data = {
        "nombre": costo_indirecto.nombre,
        "unidad_cobro": costo_indirecto.unidad_cobro,
        "costo_por_unidad": str(costo_indirecto.costo_por_unidad),
        "status": costo_indirecto.status,
        "notas": costo_indirecto.notas,
    }
    if request.method == "POST":
        form_data = {
            "nombre": request.POST.get("nombre", "").strip(),
            "unidad_cobro": request.POST.get("unidad_cobro", UnidadCobro.HORA).strip(),
            "costo_por_unidad": request.POST.get("costo_por_unidad", "").strip(),
            "status": request.POST.get("status", Status.EN_PROCESO).strip(),
            "notas": request.POST.get("notas", "").strip(),
        }
        errors = {}
        if not form_data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        if form_data["unidad_cobro"] not in UNIDAD_COBRO_VALUES:
            errors["unidad_cobro"] = "Selecciona una unidad de cobro válida."
        if form_data["status"] not in STATUS_VALUES:
            errors["status"] = "Selecciona un estado válido."

        costo = _parse_decimal(form_data["costo_por_unidad"], "costo_por_unidad", errors)
        if costo is not None and costo < 0:
            errors["costo_por_unidad"] = "El costo no puede ser negativo."
        if costo is not None and form_data["status"] == Status.ACTIVO and costo <= 0:
            errors["costo_por_unidad"] = "Para estado activo el costo debe ser mayor que 0."

        if errors:
            return render(
                request,
                "catalog/costos_indirectos/costoindirecto_form.html",
                {
                    "form_data": form_data,
                    "status_choices": _status_choices(),
                    "unidad_cobro_choices": _unidad_cobro_choices(),
                    "costo_indirecto": costo_indirecto,
                    **form_error_context(errors),
                },
            )

        costo_indirecto.nombre = form_data["nombre"]
        costo_indirecto.unidad_cobro = form_data["unidad_cobro"]
        costo_indirecto.costo_por_unidad = costo
        costo_indirecto.status = form_data["status"]
        costo_indirecto.notas = form_data["notas"]
        costo_indirecto.full_clean()
        costo_indirecto.save()
        messages.success(request, "Costo indirecto actualizado correctamente.")
        return redirect("catalog:costoindirecto_list")

    return render(
        request,
        "catalog/costos_indirectos/costoindirecto_form.html",
        {
            "form_data": form_data,
            "status_choices": _status_choices(),
            "unidad_cobro_choices": _unidad_cobro_choices(),
            "costo_indirecto": costo_indirecto,
        },
    )


@catalog_access
def costoindirecto_delete(request, pk):
    costo_indirecto = get_object_or_404(CostoIndirecto, pk=pk, owner=request.user)
    if request.method == "POST":
        costo_indirecto.delete()
        messages.success(request, "Costo indirecto eliminado correctamente.")
        return redirect("catalog:costoindirecto_list")
    return render(
        request,
        "catalog/costos_indirectos/costoindirecto_delete.html",
        {"costo_indirecto": costo_indirecto},
    )
