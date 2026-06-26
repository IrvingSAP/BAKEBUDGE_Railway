import re

from django.contrib import messages
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import UserProfile
from apps.administration.decorators import master_access
from apps.core.form_validation import form_error_context
from apps.core.models import Moneda

CODIGO_PATTERN = re.compile(r"^[A-Z]{3}$")

MONEDA_FIELD_LABELS = {
    "codigo": "Código",
    "nombre": "Nombre",
    "simbolo": "Símbolo",
    "decimales": "Decimales",
    "activa": "Activa",
    "orden": "Orden",
}


def _required_message(field_name):
    label = MONEDA_FIELD_LABELS.get(field_name, field_name)
    return f"El campo «{label}» es obligatorio."


def _parse_bool(value):
    return value in {"1", "true", "on", "si", "sí"}


def _normalize_codigo(value):
    return (value or "").strip().upper()


def _form_defaults(moneda=None):
    if moneda is None:
        return {
            "codigo": "",
            "nombre": "",
            "simbolo": "",
            "decimales": "2",
            "activa": True,
            "orden": "0",
        }
    return {
        "codigo": moneda.codigo,
        "nombre": moneda.nombre,
        "simbolo": moneda.simbolo,
        "decimales": str(moneda.decimales),
        "activa": moneda.activa,
        "orden": str(moneda.orden),
    }


def _validate_moneda_form(form_data, errors, *, is_create):
    codigo = _normalize_codigo(form_data.get("codigo"))
    form_data["codigo"] = codigo

    if is_create:
        if not codigo:
            errors["codigo"] = _required_message("codigo")
        elif not CODIGO_PATTERN.match(codigo):
            errors["codigo"] = "El código debe tener exactamente 3 letras mayúsculas (ISO 4217)."
        elif Moneda.objects.filter(codigo=codigo).exists():
            errors["codigo"] = f"Ya existe una moneda con código «{codigo}»."

    if not form_data.get("nombre", "").strip():
        errors["nombre"] = _required_message("nombre")

    if not form_data.get("simbolo", "").strip():
        errors["simbolo"] = _required_message("simbolo")

    try:
        decimales = int(form_data.get("decimales") or "0")
        if decimales < 0 or decimales > 6:
            raise ValueError
        form_data["decimales"] = str(decimales)
    except ValueError:
        errors["decimales"] = "Los decimales deben ser un entero entre 0 y 6."

    try:
        orden = int(form_data.get("orden") or "0")
        if orden < 0:
            raise ValueError
        form_data["orden"] = str(orden)
    except ValueError:
        errors["orden"] = "El orden debe ser un entero mayor o igual a 0."


@master_access
def moneda_list(request):
    monedas = (
        Moneda.objects.annotate(perfiles_count=Count("perfiles"))
        .order_by("orden", "codigo")
    )
    return render(
        request,
        "administration/monedas/moneda_list.html",
        {"monedas": monedas},
    )


@master_access
def moneda_create(request):
    form_data = _form_defaults()
    if request.method == "POST":
        form_data = {
            "codigo": request.POST.get("codigo", ""),
            "nombre": request.POST.get("nombre", "").strip(),
            "simbolo": request.POST.get("simbolo", "").strip(),
            "decimales": request.POST.get("decimales", "2").strip(),
            "activa": _parse_bool(request.POST.get("activa", "")),
            "orden": request.POST.get("orden", "0").strip(),
        }
        errors = {}
        _validate_moneda_form(form_data, errors, is_create=True)
        if errors:
            return render(
                request,
                "administration/monedas/moneda_form.html",
                {"form_data": form_data, **form_error_context(errors)},
            )

        Moneda.objects.create(
            codigo=form_data["codigo"],
            nombre=form_data["nombre"],
            simbolo=form_data["simbolo"],
            decimales=int(form_data["decimales"]),
            activa=form_data["activa"],
            orden=int(form_data["orden"]),
        )
        messages.success(request, f"Moneda «{form_data['codigo']}» creada correctamente.")
        return redirect("administration:moneda_list")

    return render(request, "administration/monedas/moneda_form.html", {"form_data": form_data})


@master_access
def moneda_edit(request, codigo):
    moneda = get_object_or_404(Moneda, codigo=_normalize_codigo(codigo))
    form_data = _form_defaults(moneda)

    if request.method == "POST":
        form_data = {
            "codigo": moneda.codigo,
            "nombre": request.POST.get("nombre", "").strip(),
            "simbolo": request.POST.get("simbolo", "").strip(),
            "decimales": request.POST.get("decimales", str(moneda.decimales)).strip(),
            "activa": _parse_bool(request.POST.get("activa", "")),
            "orden": request.POST.get("orden", str(moneda.orden)).strip(),
        }
        errors = {}
        _validate_moneda_form(form_data, errors, is_create=False)
        if errors:
            return render(
                request,
                "administration/monedas/moneda_form.html",
                {
                    "form_data": form_data,
                    "moneda": moneda,
                    **form_error_context(errors),
                },
            )

        moneda.nombre = form_data["nombre"]
        moneda.simbolo = form_data["simbolo"]
        moneda.decimales = int(form_data["decimales"])
        moneda.activa = form_data["activa"]
        moneda.orden = int(form_data["orden"])
        moneda.save()
        messages.success(request, f"Moneda «{moneda.codigo}» actualizada correctamente.")
        return redirect("administration:moneda_list")

    return render(
        request,
        "administration/monedas/moneda_form.html",
        {"form_data": form_data, "moneda": moneda},
    )


@master_access
def moneda_delete(request, codigo):
    moneda = get_object_or_404(Moneda, codigo=_normalize_codigo(codigo))
    perfiles_count = UserProfile.objects.filter(moneda=moneda).count()

    if request.method == "POST":
        if perfiles_count > 0:
            return render(
                request,
                "administration/monedas/moneda_delete.html",
                {
                    "moneda": moneda,
                    "perfiles_count": perfiles_count,
                    "error_tipo": "ER",
                    "message_modal": (
                        f"No puedes eliminar «{moneda.codigo}» porque {perfiles_count} "
                        "perfil(es) la usan como moneda preferida."
                    ),
                },
            )
        try:
            moneda.delete()
            messages.success(request, f"Moneda «{moneda.codigo}» eliminada correctamente.")
        except ProtectedError:
            messages.error(
                request,
                f"No se puede eliminar «{moneda.codigo}» porque está referenciada en el sistema.",
            )
        return redirect("administration:moneda_list")

    return render(
        request,
        "administration/monedas/moneda_delete.html",
        {"moneda": moneda, "perfiles_count": perfiles_count},
    )
