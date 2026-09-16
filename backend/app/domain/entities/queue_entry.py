from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.queue_status import QueueStatus


@dataclass(slots=True)
class QueueEntry:
    id: int | None
    restaurant_id: int
    name: str
    phone: str
    party_size: int
    status: QueueStatus
    created_at: datetime
    called_at: datetime | None = None
    seated_at: datetime | None = None
    cancelled_at: datetime | None = None

    def transition_to(self, new_status: QueueStatus, at: datetime) -> None:
        allowed = {
            QueueStatus.WAITING: {QueueStatus.CALLED, QueueStatus.CANCELLED},
            QueueStatus.CALLED: {QueueStatus.SEATED, QueueStatus.CANCELLED, QueueStatus.NO_SHOW},
        }
        if new_status not in allowed.get(self.status, set()):
            raise ValueError(f"Invalid transition {self.status.value} -> {new_status.value}")
        self.status = new_status
        if new_status == QueueStatus.CALLED: self.called_at = at
        elif new_status == QueueStatus.SEATED: self.seated_at = at
        elif new_status in (QueueStatus.CANCELLED, QueueStatus.NO_SHOW): self.cancelled_at = at
