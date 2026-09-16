import logging

from app.domain.ports.email_notification import EmailMessage


logger = logging.getLogger(__name__)


class EmailLogNotification:
    """Adaptador seguro para MVP: registra el correo, pero no lo envía."""

    def send(self, message: EmailMessage) -> None:
        logger.info("Email pendiente de proveedor: recipient=%s subject=%s", message.recipient, message.subject)
