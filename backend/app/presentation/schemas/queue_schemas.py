from datetime import date as Date, datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.enums.queue_status import QueueStatus


class JoinQueueRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120, description="Nombre de la persona de contacto.", examples=["Carla M."])
    phone: str = Field(min_length=7, max_length=30, pattern=r"^\+?[0-9\s\-()]+$", description="Teléfono con prefijo internacional opcional; se aceptan espacios, guiones y paréntesis.", examples=["+51987234567"])
    party_size: int = Field(ge=1, le=20, description="Cantidad de personas del grupo (entre 1 y 20).", examples=[4])

    @field_validator("name")
    @classmethod
    def not_blank(cls, value: str):
        if not value.strip(): raise ValueError("must not be blank")
        if any(not (character.isalpha() or character in " '") for character in value.strip()):
            raise ValueError("name may contain only letters, spaces and apostrophes")
        return value

    @field_validator("phone")
    @classmethod
    def has_enough_digits(cls, value: str):
        if sum(character.isdigit() for character in value) < 7:
            raise ValueError("phone must contain at least 7 digits")
        return value


class QueueEntryResponse(BaseModel):
    id: int = Field(description="Identificador único del ingreso.")
    restaurant_id: int
    name: str
    phone: str
    party_size: int
    status: QueueStatus = Field(description="WAITING, CALLED, SEATED, CANCELLED o NO_SHOW.")
    created_at: datetime = Field(description="Fecha y hora de ingreso, almacenada en UTC.")
    called_at: datetime | None = Field(description="Fecha y hora de llamada en UTC.")
    seated_at: datetime | None = None
    cancelled_at: datetime | None = None
    position: int | None = Field(default=None, description="Posición actual entre los grupos WAITING.")

    model_config = {"from_attributes": True}


class QueueResponse(BaseModel):
    entries: list[QueueEntryResponse]


class RestaurantResponse(BaseModel):
    id: int
    name: str
    country_code: str
    phone_country_code: str
    timezone: str


class DailyReportResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    date: Date = Field(description="Día calendario local del restaurante en formato YYYY-MM-DD.", examples=["2026-09-15"])
    joined_count: int
    seated_count: int
    cancelled_count: int
    no_show_count: int
    average_wait_minutes: float | None = Field(description="Espera media en minutos para grupos SEATED; null si no hay datos.")
