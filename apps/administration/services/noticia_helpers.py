"""Utilidades de validación para formularios de Noticia."""

from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile
from apps.noticias.models import Noticia

User = get_user_model()

NOTICIA_FIELD_LABELS = {
    "alcance": "Alcance",
    "tipo": "Tipo",
    "titulo": "Título",
    "detalle": "Detalle",
    "resumen": "Resumen",
    "fecha_noticia": "Fecha noticia",
    "visible_desde": "Visible desde",
    "visible_hasta": "Visible hasta",
    "status": "Estado",
    "orden": "Orden",
    "enlace_interno": "Enlace interno",
    "enlace_externo": "Enlace externo",
    "destinatarios": "Destinatarios",
}


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        from datetime import date

        return date.fromisoformat(value)
    except ValueError:
        return None


def get_destinatario_users():
    return (
        User.objects.filter(profile__user_type=UserProfile.UserType.USER)
        .select_related("profile")
        .order_by("username")
    )


def parse_destinatarios(post_values):
    ids = []
    for raw in post_values or []:
        try:
            ids.append(int(raw))
        except (TypeError, ValueError):
            continue
    return ids


def parse_form_post(request, *, noticia=None):
    destacada = request.POST.get("destacada") in {"1", "on", "true"}
    return {
        "alcance": request.POST.get("alcance", noticia.alcance if noticia else Noticia.Alcance.GLOBAL),
        "tipo": request.POST.get("tipo", noticia.tipo if noticia else "").strip(),
        "titulo": request.POST.get("titulo", noticia.titulo if noticia else "").strip(),
        "detalle": request.POST.get("detalle", noticia.detalle if noticia else "").strip(),
        "resumen": request.POST.get("resumen", noticia.resumen if noticia else "").strip(),
        "fecha_noticia": parse_date(request.POST.get("fecha_noticia")),
        "visible_desde": parse_date(request.POST.get("visible_desde")),
        "visible_hasta": parse_date(request.POST.get("visible_hasta")),
        "status": request.POST.get("status", noticia.status if noticia else Noticia.Status.ACTIVO),
        "destacada": destacada,
        "orden": request.POST.get("orden", str(noticia.orden) if noticia else "0"),
        "enlace_interno": request.POST.get(
            "enlace_interno",
            noticia.enlace_interno if noticia else "",
        ).strip(),
        "enlace_externo": request.POST.get(
            "enlace_externo",
            noticia.enlace_externo if noticia else "",
        ).strip(),
        "destinatarios": parse_destinatarios(request.POST.getlist("destinatarios")),
    }


def serialize_form_data(form_data):
    result = dict(form_data)
    for key in ("fecha_noticia", "visible_desde", "visible_hasta"):
        value = result.get(key)
        if value and hasattr(value, "isoformat"):
            result[key] = value.isoformat()
    if result.get("destinatarios") is not None:
        result["destinatarios"] = [str(pk) for pk in result["destinatarios"]]
    return result


def validate_form(form_data, errors):
    alcance = form_data.get("alcance") or ""
    if alcance not in dict(Noticia.Alcance.choices):
        errors["alcance"] = "Selecciona un alcance válido."

    tipo = form_data.get("tipo") or ""
    if not tipo:
        errors["tipo"] = "El tipo es obligatorio."
    elif len(tipo) > 20:
        errors["tipo"] = "El tipo no puede superar 20 caracteres."

    if not form_data.get("titulo"):
        errors["titulo"] = "El título es obligatorio."
    elif len(form_data["titulo"]) > 200:
        errors["titulo"] = "El título no puede superar 200 caracteres."

    form_data["detalle"] = (form_data.get("detalle") or "").strip()

    resumen = form_data.get("resumen") or ""
    if len(resumen) > 300:
        errors["resumen"] = "El resumen no puede superar 300 caracteres."

    if not form_data.get("fecha_noticia"):
        errors["fecha_noticia"] = "La fecha de la noticia es obligatoria."

    if not form_data.get("visible_desde"):
        errors["visible_desde"] = "Indica la fecha «visible desde»."
    if not form_data.get("visible_hasta"):
        errors["visible_hasta"] = "Indica la fecha «visible hasta»."

    if (
        form_data.get("visible_desde")
        and form_data.get("visible_hasta")
        and form_data["visible_hasta"] < form_data["visible_desde"]
    ):
        errors["visible_hasta"] = "La fecha «visible hasta» debe ser posterior o igual a «visible desde»."

    status = form_data.get("status") or ""
    if status not in dict(Noticia.Status.choices):
        errors["status"] = "Selecciona un estado válido."

    try:
        orden = int(form_data.get("orden") or "0")
        if orden < 0:
            raise ValueError
        form_data["orden"] = orden
    except (TypeError, ValueError):
        errors["orden"] = "El orden debe ser un entero ≥ 0."

    enlace_interno = form_data.get("enlace_interno") or ""
    if len(enlace_interno) > 200:
        errors["enlace_interno"] = "El enlace interno no puede superar 200 caracteres."

    enlace_externo = (form_data.get("enlace_externo") or "").strip()
    form_data["enlace_externo"] = enlace_externo
    if enlace_externo:
        from django.core.validators import URLValidator

        validator = URLValidator()
        try:
            validator(enlace_externo)
        except Exception:
            errors["enlace_externo"] = "Ingresa una URL externa válida."

    destinatarios = form_data.get("destinatarios") or []
    if alcance == Noticia.Alcance.PERSONAL:
        if not destinatarios:
            errors["destinatarios"] = "Selecciona al menos un destinatario para noticias personales."
        else:
            valid_ids = set(
                User.objects.filter(
                    pk__in=destinatarios,
                    profile__user_type=UserProfile.UserType.USER,
                ).values_list("pk", flat=True)
            )
            if len(valid_ids) != len(set(destinatarios)):
                errors["destinatarios"] = "Uno o más destinatarios no son válidos."
            form_data["destinatarios"] = list(valid_ids)
    else:
        form_data["destinatarios"] = []


def form_defaults(noticia=None):
    if noticia:
        return {
            "alcance": noticia.alcance,
            "tipo": noticia.tipo,
            "titulo": noticia.titulo,
            "detalle": noticia.detalle,
            "resumen": noticia.resumen,
            "fecha_noticia": noticia.fecha_noticia.isoformat() if noticia.fecha_noticia else "",
            "visible_desde": noticia.visible_desde.isoformat() if noticia.visible_desde else "",
            "visible_hasta": noticia.visible_hasta.isoformat() if noticia.visible_hasta else "",
            "status": noticia.status,
            "destacada": noticia.destacada,
            "orden": str(noticia.orden),
            "enlace_interno": noticia.enlace_interno,
            "enlace_externo": noticia.enlace_externo,
            "destinatarios": list(noticia.destinatarios.values_list("pk", flat=True)),
        }

    from django.utils import timezone

    today = timezone.localdate().isoformat()
    return {
        "alcance": Noticia.Alcance.GLOBAL,
        "tipo": "",
        "titulo": "",
        "detalle": "",
        "resumen": "",
        "fecha_noticia": today,
        "visible_desde": today,
        "visible_hasta": today,
        "status": Noticia.Status.ACTIVO,
        "destacada": False,
        "orden": "0",
        "enlace_interno": "",
        "enlace_externo": "",
        "destinatarios": [],
    }


def apply_form_to_noticia(noticia, form_data, acting_user):
    noticia.alcance = form_data["alcance"]
    noticia.tipo = form_data["tipo"]
    noticia.titulo = form_data["titulo"]
    noticia.detalle = form_data.get("detalle") or ""
    noticia.resumen = form_data.get("resumen") or ""
    noticia.fecha_noticia = form_data["fecha_noticia"]
    noticia.visible_desde = form_data["visible_desde"]
    noticia.visible_hasta = form_data["visible_hasta"]
    noticia.status = form_data["status"]
    noticia.destacada = form_data.get("destacada", False)
    noticia.orden = form_data.get("orden", 0)
    noticia.enlace_interno = form_data.get("enlace_interno") or ""
    noticia.enlace_externo = form_data.get("enlace_externo") or ""
    noticia.updated_by = acting_user
    return form_data.get("destinatarios") or []


COPY_TITULO_SUFFIX = " (copia)"
TITULO_MAX_LENGTH = 200


def copy_titulo(titulo):
    if len(titulo) + len(COPY_TITULO_SUFFIX) <= TITULO_MAX_LENGTH:
        return titulo + COPY_TITULO_SUFFIX
    return titulo[: TITULO_MAX_LENGTH - len(COPY_TITULO_SUFFIX)] + COPY_TITULO_SUFFIX


def duplicate_noticia(source, acting_user):
    """Clona una noticia (contenido + destinatarios) como registro nuevo."""
    destinatario_ids = list(source.destinatarios.values_list("pk", flat=True))
    clone = Noticia(
        alcance=source.alcance,
        tipo=source.tipo,
        titulo=copy_titulo(source.titulo),
        detalle=source.detalle,
        resumen=source.resumen,
        fecha_noticia=source.fecha_noticia,
        visible_desde=source.visible_desde,
        visible_hasta=source.visible_hasta,
        status=source.status,
        destacada=source.destacada,
        orden=source.orden,
        enlace_interno=source.enlace_interno,
        enlace_externo=source.enlace_externo,
        created_by=acting_user,
        updated_by=acting_user,
    )
    clone.save()
    if destinatario_ids:
        clone.destinatarios.set(destinatario_ids)
    return clone
