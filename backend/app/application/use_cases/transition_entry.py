from datetime import datetime, timezone

from app.application.exceptions import InvalidStateError, NotFoundError
from app.domain.enums.queue_status import QueueStatus


class TransitionEntry:
    def __init__(self, queue): self.queue = queue

    def execute(self, entry_id: int, expected: QueueStatus, new_status: QueueStatus):
        entry = self.queue.get(entry_id)
        if entry is None: raise NotFoundError("Queue entry not found")
        if entry.status != expected: raise InvalidStateError(f"Entry must be {expected.value}")
        try: entry.transition_to(new_status, datetime.now(timezone.utc))
        except ValueError as exc: raise InvalidStateError(str(exc)) from exc
        return self.queue.transition(entry_id, expected, new_status, datetime.now(timezone.utc))
