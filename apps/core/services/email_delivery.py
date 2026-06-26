"""Envío transaccional — consola en dev; SMTP/Resend en producción."""

from django.conf import settings
from django.core.mail import send_mail


def send_transactional_email(*, to: str, subject: str, body: str) -> None:
    delivery = getattr(settings, "EMAIL_DELIVERY", "console")

    if delivery == "console":
        print(
            f"\n--- BAKEBUDGE EMAIL ---\n"
            f"Para: {to}\n"
            f"Asunto: {subject}\n"
            f"{body}\n"
            f"-----------------------\n"
        )
        return

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        fail_silently=False,
    )
