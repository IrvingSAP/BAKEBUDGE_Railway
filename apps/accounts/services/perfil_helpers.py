"""Parseo y validación del formulario de perfil del usuario conectado."""

from decimal import Decimal

from apps.core.form_validation import (
    field_label,
    form_error_context,
    parse_decimal,
    required_field_message,
)
from apps.core.models import Moneda

PERFIL_FIELD_LABELS = {
    "nombre_negocio": "Nombre de la repostería",
    "moneda": "Moneda",
    "margen_objetivo_pct": "Margen objetivo (%)",
    "unidad_peso_default": "Unidad de peso",
    "unidad_volumen_default": "Unidad de volumen",
    "unidad_conteo_default": "Unidad de conteo",
}

UNIDAD_PESO_CHOICES = ("g", "kg")
UNIDAD_VOLUMEN_CHOICES = ("ml", "L")
UNIDAD_CONTEO_CHOICES = ("unidad",)

MARGEN_MAX = Decimal("999.99")


def _required(field_name):
    return required_field_message(field_name, PERFIL_FIELD_LABELS)


def monedas_for_select(profile):
    monedas = list(Moneda.objects.filter(activa=True).order_by("orden", "codigo"))
    current = profile.moneda
    if current and not any(m.codigo == current.codigo for m in monedas):
        monedas.insert(0, current)
    if not monedas:
        monedas = list(Moneda.objects.order_by("orden", "codigo")[:1])
    return monedas


def form_defaults_from_profile(profile):
    return {
        "nombre_negocio": profile.nombre_negocio,
        "moneda": profile.moneda_id,
        "margen_objetivo_pct": format(profile.margen_objetivo_pct, "f"),
        "unidad_peso_default": profile.unidad_peso_default,
        "unidad_volumen_default": profile.unidad_volumen_default,
        "unidad_conteo_default": profile.unidad_conteo_default,
    }


def parse_perfil_post(request):
    return {
        "nombre_negocio": (request.POST.get("nombre_negocio") or "").strip(),
        "moneda": (request.POST.get("moneda") or "").strip().upper(),
        "margen_objetivo_pct": (request.POST.get("margen_objetivo_pct") or "").strip(),
        "unidad_peso_default": (request.POST.get("unidad_peso_default") or "").strip(),
        "unidad_volumen_default": (request.POST.get("unidad_volumen_default") or "").strip(),
        "unidad_conteo_default": (request.POST.get("unidad_conteo_default") or "").strip(),
    }


def validate_perfil_form(form_data, errors, *, profile):
    nombre = form_data.get("nombre_negocio") or ""
    if not nombre:
        errors["nombre_negocio"] = _required("nombre_negocio")
    elif len(nombre) > 150:
        errors["nombre_negocio"] = "El nombre de la repostería no puede superar 150 caracteres."

    moneda_codigo = form_data.get("moneda") or ""
    if not moneda_codigo:
        errors["moneda"] = _required("moneda")
    else:
        allowed_codes = {m.codigo for m in monedas_for_select(profile)}
        if moneda_codigo not in allowed_codes:
            errors["moneda"] = f"La moneda «{moneda_codigo}» no está disponible."

    margen = parse_decimal(
        form_data.get("margen_objetivo_pct"),
        "margen_objetivo_pct",
        errors,
        PERFIL_FIELD_LABELS,
    )
    if margen is not None:
        if margen < 0:
            errors["margen_objetivo_pct"] = (
                f"El «{field_label('margen_objetivo_pct', PERFIL_FIELD_LABELS)}» debe ser ≥ 0."
            )
        elif margen > MARGEN_MAX:
            errors["margen_objetivo_pct"] = (
                f"El «{field_label('margen_objetivo_pct', PERFIL_FIELD_LABELS)}» no puede superar {MARGEN_MAX}."
            )
        else:
            form_data["margen_objetivo_pct"] = margen

    peso = form_data.get("unidad_peso_default") or ""
    if peso not in UNIDAD_PESO_CHOICES:
        errors["unidad_peso_default"] = "Selecciona una unidad de peso válida."

    volumen = form_data.get("unidad_volumen_default") or ""
    if volumen not in UNIDAD_VOLUMEN_CHOICES:
        errors["unidad_volumen_default"] = "Selecciona una unidad de volumen válida."

    conteo = form_data.get("unidad_conteo_default") or ""
    if conteo not in UNIDAD_CONTEO_CHOICES:
        errors["unidad_conteo_default"] = "Selecciona una unidad de conteo válida."


def apply_perfil_form(profile, form_data):
    profile.nombre_negocio = form_data["nombre_negocio"]
    profile.moneda_id = form_data["moneda"]
    profile.margen_objetivo_pct = form_data["margen_objetivo_pct"]
    profile.unidad_peso_default = form_data["unidad_peso_default"]
    profile.unidad_volumen_default = form_data["unidad_volumen_default"]
    profile.unidad_conteo_default = form_data["unidad_conteo_default"]
    profile.save(
        update_fields=[
            "nombre_negocio",
            "moneda",
            "margen_objetivo_pct",
            "unidad_peso_default",
            "unidad_volumen_default",
            "unidad_conteo_default",
            "updated_at",
        ]
    )


__all__ = [
    "UNIDAD_CONTEO_CHOICES",
    "UNIDAD_PESO_CHOICES",
    "UNIDAD_VOLUMEN_CHOICES",
    "apply_perfil_form",
    "form_defaults_from_profile",
    "form_error_context",
    "monedas_for_select",
    "parse_perfil_post",
    "validate_perfil_form",
]
