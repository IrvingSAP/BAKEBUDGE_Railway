from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.administration.decorators import master_access
from apps.public_site.models import MensajeContacto


def _get_mensaje(pk):
    return get_object_or_404(MensajeContacto, pk=pk)


@master_access
def mensajecontacto_list(request):
    mensajes = MensajeContacto.objects.all()
    return render(
        request,
        "administration/mensajes_contacto/mensajecontacto_list.html",
        {"mensajes": mensajes},
    )


@master_access
def mensajecontacto_detail(request, pk):
    mensaje = _get_mensaje(pk)

    if request.method == "POST" and request.POST.get("marcar_leido"):
        if mensaje.is_pendiente:
            mensaje.marcar_leido()
            messages.success(request, "Mensaje marcado como leído.")
        return redirect("administration:mensajecontacto_detail", pk=mensaje.pk)

    return render(
        request,
        "administration/mensajes_contacto/mensajecontacto_detail.html",
        {"mensaje": mensaje},
    )


@master_access
def mensajecontacto_delete(request, pk):
    mensaje = _get_mensaje(pk)

    if request.method == "POST":
        titulo = mensaje.nombre
        mensaje.delete()
        messages.success(request, f"Mensaje de «{titulo}» eliminado correctamente.")
        return redirect("administration:mensajecontacto_list")

    return render(
        request,
        "administration/mensajes_contacto/mensajecontacto_delete.html",
        {"mensaje": mensaje},
    )
