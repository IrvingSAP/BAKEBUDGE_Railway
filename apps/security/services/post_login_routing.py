"""Destino tras completar el wizard de seguridad (primer acceso vs. habitual)."""

from django.urls import reverse


def resolve_post_security_redirect(profile):
    """
    Tras login completo post-TOTP.
    Primer acceso a /app/ → feed de Noticias (bienvenida configurada por Master).
    Accesos siguientes → Dashboard.
    """
    if not profile.can_access_app:
        return reverse("dashboard:access_denied")

    if not profile.primer_acceso_app_completado:
        return reverse("noticias:feed")

    return reverse("dashboard:home")


def mark_primer_acceso_completado(profile) -> bool:
    """Marca el primer acceso y devuelve True si era la primera vez."""
    if profile.primer_acceso_app_completado:
        return False
    profile.primer_acceso_app_completado = True
    profile.save(update_fields=["primer_acceso_app_completado", "updated_at"])
    return True
