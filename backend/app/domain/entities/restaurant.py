from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Restaurant:
    id: int | None
    name: str
    country_code: str
    phone_country_code: str
    timezone: str
    created_at: datetime
