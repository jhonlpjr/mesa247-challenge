from sqlalchemy.orm import Session

from app.infrastructure.database.models.restaurant_model import RestaurantModel
from app.infrastructure.repositories.sqlalchemy_mappers import to_restaurant


class SQLAlchemyRestaurantRepository:
    def __init__(self, session: Session): self.session = session

    def get(self, restaurant_id: int):
        model = self.session.get(RestaurantModel, restaurant_id)
        return to_restaurant(model) if model else None
