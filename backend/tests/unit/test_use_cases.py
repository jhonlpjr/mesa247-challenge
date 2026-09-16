from datetime import datetime, timezone, timedelta

from app.application.use_cases.call_next import CallNext
from app.application.use_cases.get_queue_entry import GetQueueEntry
from app.application.use_cases.get_restaurant_queue import GetRestaurantQueue
from app.application.use_cases.join_queue import JoinQueue
from app.domain.entities.restaurant import Restaurant
from app.domain.enums.queue_status import QueueStatus


class FakeRestaurants:
    def __init__(self): self.items = {1: Restaurant(1, "Demo", "PE", "+51", "America/Lima", datetime.now(timezone.utc))}
    def get(self, restaurant_id): return self.items.get(restaurant_id)


class FakeQueue:
    def __init__(self): self.items = []
    def add(self, entry): entry.id = len(self.items) + 1; self.items.append(entry); return entry
    def get(self, entry_id): return next((e for e in self.items if e.id == entry_id), None)
    def list_waiting(self, restaurant_id): return sorted((e for e in self.items if e.restaurant_id == restaurant_id and e.status == QueueStatus.WAITING), key=lambda e: (e.created_at, e.id))
    def list_active(self, restaurant_id): return self.list_waiting(restaurant_id)
    def entries_between(self, restaurant_id, start, end): return [e for e in self.items if e.restaurant_id == restaurant_id and start <= e.created_at.replace(tzinfo=start.tzinfo) < end]
    def position(self, entry):
        return next((i for i, e in enumerate(self.list_waiting(entry.restaurant_id), 1) if e.id == entry.id), None)
    def call_next(self, restaurant_id, called_at):
        waiting = self.list_waiting(restaurant_id)
        if not waiting: return None
        waiting[0].status, waiting[0].called_at = QueueStatus.CALLED, called_at
        return waiting[0]


def test_join_enters_waiting_and_position_follows_arrival():
    restaurants, queue = FakeRestaurants(), FakeQueue()
    join = JoinQueue(restaurants, queue)
    first = join.execute(1, " Ana ", "999999999", 2)
    second = join.execute(1, "Bob", "888888888", 3)
    assert first.status == QueueStatus.WAITING and first.name == "Ana"
    assert GetQueueEntry(queue).execute(second.id)[1] == 2


def test_call_next_sets_called_at_and_does_not_reselect_called_entry():
    restaurants, queue = FakeRestaurants(), FakeQueue()
    join = JoinQueue(restaurants, queue)
    join.execute(1, "Ana", "999999999", 2)
    called = CallNext(restaurants, queue).execute(1)
    assert called.status == QueueStatus.CALLED and called.called_at is not None
    assert CallNext(restaurants, queue).execute(1) is None


def test_get_restaurant_queue_supports_iana_timezones():
    restaurants, queue = FakeRestaurants(), FakeQueue()
    entry = JoinQueue(restaurants, queue).execute(1, "Ana", "999999999", 2)

    result = GetRestaurantQueue(restaurants, queue).execute(1)

    assert result == [entry]
