import threading
import logging
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.conf import settings

logger = logging.getLogger(__name__)


def _send_inquiry_email(
    *,
    equipment_name: str,
    owner_email: str,
    customer_name: str,
    customer_email: str,
    subject: str,
    message: str,
):
    """Low-level email sender (sync, internal use only)"""

    email_message = (
        f"New equipment inquiry\n\n"
        f"Equipment: {equipment_name}\n"
        f"Customer: {customer_name}\n"
        f"Email: {customer_email}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}"
    )
    """
    send_mail(
        subject=f"Inquiry about {equipment_name}",
        message=email_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[owner_email],
        reply_to=[customer_email],
        fail_silently=False,
    )
    """
    reply_to=customer_email
    recipient=owner_email

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        reply_to=[reply_to],
    )
    email.send(fail_silently=False)


def send_inquiry_email_async(**kwargs):
    """
    Fire-and-forget email sender.
    Thread-based now, Celery-ready later.
    """

    def task():
        try:
            _send_inquiry_email(**kwargs)
        except Exception:
            logger.exception("Failed to send equipment inquiry email")

    threading.Thread(target=task, daemon=True).start()
