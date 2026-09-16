from app.application.exceptions import NotFoundError
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.domain.repositories.queue_repository import QueueRepository
from app.domain.repositories.restaurant_repository import RestaurantRepository


class GetRestaurantQueue:
    def __init__(self, restaurants: RestaurantRepository, queue: QueueRepository):
        self.restaurants, self.queue = restaurants, queue

    def execute(self, restaurant_id: int):
        restaurant = self.restaurants.get(restaurant_id)
        if restaurant is None:
            raise NotFoundError("Restaurant not found")
        waiting = self.queue.list_active(restaurant_id)
        zone = ZoneInfo(restaurant.timezone)
        local_day = datetime.now(timezone.utc).astimezone(zone).date()
        return [entry for entry in waiting if (entry.created_at.replace(tzinfo=timezone.utc) if entry.created_at.tzinfo is None else entry.created_at).astimezone(zone).date() == local_day]
