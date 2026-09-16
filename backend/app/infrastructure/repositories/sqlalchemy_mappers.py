from app.domain.entities.queue_entry import QueueEntry
from app.domain.entities.restaurant import Restaurant
from app.domain.enums.queue_status import QueueStatus
from app.infrastructure.database.models.queue_entry_model import QueueEntryModel
from app.infrastructure.database.models.restaurant_model import RestaurantModel


def to_entry(model: QueueEntryModel) -> QueueEntry:
    return QueueEntry(model.id, model.restaurant_id, model.name, model.phone, model.party_size,
                      QueueStatus(model.status), model.created_at, model.called_at, model.seated_at, model.cancelled_at)


def to_restaurant(model: RestaurantModel) -> Restaurant:
    return Restaurant(model.id, model.name, model.country_code, model.phone_country_code, model.timezone, model.created_at)
