from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmailMessage:
    """Mensaje neutral al proveedor para futuras notificaciones por correo."""

    recipient: str
    subject: str
    html_body: str
    text_body: str


class EmailNotificationPort(Protocol):
    """Contrato que podrán implementar SMTP, SendGrid, SES u otro proveedor."""

    def send(self, message: EmailMessage) -> None: ...
