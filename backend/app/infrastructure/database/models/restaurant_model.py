from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class RestaurantModel(Base):
    __tablename__ = "restaurants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, server_default="PE")
    phone_country_code: Mapped[str] = mapped_column(String(4), nullable=False, server_default="+51")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="America/Lima")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    queue_entries = relationship("QueueEntryModel", back_populates="restaurant")
