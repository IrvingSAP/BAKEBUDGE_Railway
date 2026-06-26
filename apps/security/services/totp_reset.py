"""Reset / re-enrolamiento 2FA."""

from django.utils import timezone

from . import email_confirmation


def reset_two_factor(profile) -> None:
    profile.email_confirmed = False
    profile.tfa_verified = False
    profile.totp_secret = None
    profile.email_confirm_code = None
    profile.email_confirm_exp = None
    profile.last_totp_reset = timezone.now()
    profile.save(
        update_fields=[
            "email_confirmed",
            "tfa_verified",
            "totp_secret",
            "email_confirm_code",
            "email_confirm_exp",
            "last_totp_reset",
        ]
    )


def reset_and_send_email(user, profile) -> None:
    reset_two_factor(profile)
    email_confirmation.send_confirmation_email(user, profile)
