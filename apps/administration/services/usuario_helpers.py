"""Utilidades de validación y presentación para gestión de usuarios."""

from apps.accounts.models import UserProfile


def active_master_count(*, excluding_user_id=None):
    qs = UserProfile.objects.filter(
        user_type=UserProfile.UserType.MASTER,
        status=UserProfile.Status.ACTIVO,
        user__is_active=True,
    )
    if excluding_user_id:
        qs = qs.exclude(user_id=excluding_user_id)
    return qs.count()


def can_demote_master(user, new_user_type):
    profile = user.profile
    if profile.user_type != UserProfile.UserType.MASTER:
        return True, ""
    if new_user_type != UserProfile.UserType.USER:
        return True, ""
    if profile.status != UserProfile.Status.ACTIVO or not user.is_active:
        return True, ""
    if active_master_count(excluding_user_id=user.pk) >= 1:
        return True, ""
    return False, "No puedes degradar al único Master activo de la plataforma."


def can_deactivate_user(target_user, acting_user):
    if target_user.pk == acting_user.pk:
        return False, "No puedes desactivar tu propia cuenta mientras estás conectado."

    profile = target_user.profile
    if (
        profile.user_type == UserProfile.UserType.MASTER
        and profile.status == UserProfile.Status.ACTIVO
        and target_user.is_active
        and active_master_count(excluding_user_id=target_user.pk) == 0
    ):
        return False, "No puedes desactivar al único Master activo de la plataforma."

    return True, ""


def mask_totp_secret(secret):
    if not secret:
        return "—"
    if len(secret) <= 4:
        return "****"
    return f"{secret[:4]}****{secret[-4:]}"
