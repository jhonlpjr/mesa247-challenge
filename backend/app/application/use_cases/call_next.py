from datetime import datetime, timezone

from app.application.exceptions import NotFoundError
from app.domain.repositories.queue_repository import QueueRepository
from app.domain.repositories.restaurant_repository import RestaurantRepository


class CallNext:
    def __init__(self, restaurants: RestaurantRepository, queue: QueueRepository):
        self.restaurants, self.queue = restaurants, queue

    def execute(self, restaurant_id: int):
        if self.restaurants.get(restaurant_id) is None:
            raise NotFoundError("Restaurant not found")
        return self.queue.call_next(restaurant_id, datetime.now(timezone.utc))
