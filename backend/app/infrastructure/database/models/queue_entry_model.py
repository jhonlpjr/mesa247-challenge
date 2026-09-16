from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.queue_status import QueueStatus
from app.infrastructure.database.base import Base


class QueueEntryModel(Base):
    __tablename__ = "queue_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[QueueStatus] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    seated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    restaurant = relationship("RestaurantModel", back_populates="queue_entries")
    __table_args__ = (
        Index("ix_queue_entries_restaurant_status_created", "restaurant_id", "status", "created_at"),
        CheckConstraint("party_size BETWEEN 1 AND 20", name="ck_queue_entries_party_size"),
        CheckConstraint("status IN ('WAITING', 'CALLED', 'SEATED', 'CANCELLED', 'NO_SHOW')", name="ck_queue_entries_status"),
    )
