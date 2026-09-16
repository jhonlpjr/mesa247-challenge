from app.application.exceptions import NotFoundError
from app.domain.repositories.queue_repository import QueueRepository


class GetQueueEntry:
    def __init__(self, queue: QueueRepository):
        self.queue = queue

    def execute(self, entry_id: int):
        entry = self.queue.get(entry_id)
        if entry is None:
            raise NotFoundError("Queue entry not found")
        return entry, self.queue.position(entry)
