from datetime import datetime, timezone

from app.application.exceptions import NotFoundError, ValidationError
from app.application.phone import normalize_phone
from app.domain.entities.queue_entry import QueueEntry
from app.domain.enums.queue_status import QueueStatus
from app.domain.repositories.queue_repository import QueueRepository
from app.domain.repositories.restaurant_repository import RestaurantRepository


class JoinQueue:
    def __init__(self, restaurants: RestaurantRepository, queue: QueueRepository):
        self.restaurants, self.queue = restaurants, queue

    def execute(self, restaurant_id: int, name: str, phone: str, party_size: int) -> QueueEntry:
        restaurant = self.restaurants.get(restaurant_id)
        if restaurant is None:
            raise NotFoundError("Restaurant not found")
        normalized_name = name.strip()
        if not normalized_name or not phone.strip():
            raise ValidationError("name and phone are required")
        if any(not (character.isalpha() or character in " '") for character in normalized_name):
            raise ValidationError("name may contain only letters, spaces and apostrophes")
        if party_size < 1 or party_size > 20:
            raise ValidationError("party_size must be between 1 and 20")
        return self.queue.add(QueueEntry(None, restaurant_id, normalized_name, normalize_phone(phone, restaurant.phone_country_code), party_size,
                                         QueueStatus.WAITING, datetime.now(timezone.utc)))
