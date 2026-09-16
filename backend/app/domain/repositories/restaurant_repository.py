from typing import Protocol

from app.domain.entities.restaurant import Restaurant


class RestaurantRepository(Protocol):
    def get(self, restaurant_id: int) -> Restaurant | None: ...
