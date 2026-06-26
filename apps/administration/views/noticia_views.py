from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.administration.decorators import master_access
from apps.administration.services.noticia_helpers import (
    apply_form_to_noticia,
    duplicate_noticia,
    form_defaults,
    get_destinatario_users,
    parse_form_post,
    serialize_form_data,
    validate_form,
)
from apps.core.form_validation import form_error_context
from apps.noticias.models import Noticia


def _get_noticia(pk):
    return get_object_or_404(
        Noticia.objects.prefetch_related("destinatarios").select_related(
            "created_by",
            "updated_by",
        ),
        pk=pk,
    )


def _render_form(request, form_data, *, noticia=None, **extra):
    destinatarios_selected = {str(pk) for pk in (form_data.get("destinatarios") or [])}
    return render(
        request,
        "administration/noticias/noticia_form.html",
        {
            "form_data": serialize_form_data(form_data),
            "noticia": noticia,
            "destinatario_users": get_destinatario_users(),
            "destinatarios_selected": destinatarios_selected,
            **extra,
        },
    )


@master_access
def noticia_list(request):
    noticias = Noticia.objects.all().order_by("-fecha_noticia", "-created_at")
    return render(
        request,
        "administration/noticias/noticia_list.html",
        {"noticias": noticias},
    )


@master_access
def noticia_create(request):
    form_data = form_defaults()

    if request.method == "POST":
        form_data = parse_form_post(request)
        errors = {}
        validate_form(form_data, errors)

        if errors:
            return _render_form(request, form_data, **form_error_context(errors))

        noticia = Noticia(created_by=request.user, updated_by=request.user)
        destinatarios = apply_form_to_noticia(noticia, form_data, request.user)
        noticia.save()
        if destinatarios:
            noticia.destinatarios.set(destinatarios)

        messages.success(request, f"Noticia «{noticia.titulo}» creada correctamente.")
        return redirect("administration:noticia_list")

    return _render_form(request, form_data)


@master_access
def noticia_edit(request, pk):
    noticia = _get_noticia(pk)
    form_data = form_defaults(noticia)

    if request.method == "POST":
        form_data = parse_form_post(request, noticia=noticia)
        errors = {}
        validate_form(form_data, errors)

        if errors:
            return _render_form(
                request,
                form_data,
                noticia=noticia,
                **form_error_context(errors),
            )

        destinatarios = apply_form_to_noticia(noticia, form_data, request.user)
        noticia.save()
        noticia.destinatarios.set(destinatarios)

        messages.success(request, f"Noticia «{noticia.titulo}» actualizada correctamente.")
        return redirect("administration:noticia_list")

    return _render_form(request, form_data, noticia=noticia)


@master_access
def noticia_copy(request, pk):
    source = _get_noticia(pk)
    clone = duplicate_noticia(source, request.user)
    messages.success(
        request,
        f"Copia creada a partir de «{source.titulo}». Ajusta los datos y guarda.",
    )
    return redirect("administration:noticia_edit", pk=clone.pk)


@master_access
def noticia_deactivate(request, pk):
    noticia = _get_noticia(pk)

    if noticia.status == Noticia.Status.INACTIVO:
        return render(
            request,
            "administration/noticias/noticia_deactivate.html",
            {
                "noticia": noticia,
                "can_deactivate": False,
                "block_message": "Esta noticia ya está inactiva.",
            },
        )

    if request.method == "POST":
        noticia.status = Noticia.Status.INACTIVO
        noticia.updated_by = request.user
        noticia.save(update_fields=["status", "updated_by", "updated_at"])
        messages.success(request, f"Noticia «{noticia.titulo}» desactivada correctamente.")
        return redirect("administration:noticia_list")

    return render(
        request,
        "administration/noticias/noticia_deactivate.html",
        {"noticia": noticia, "can_deactivate": True},
    )
