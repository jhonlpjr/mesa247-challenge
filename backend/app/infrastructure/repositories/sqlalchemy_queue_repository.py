from datetime import datetime
from threading import Lock

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.domain.entities.queue_entry import QueueEntry
from app.domain.enums.queue_status import QueueStatus
from app.infrastructure.database.models.queue_entry_model import QueueEntryModel
from app.infrastructure.repositories.sqlalchemy_mappers import to_entry


_call_next_lock = Lock()


class SQLAlchemyQueueRepository:
    def __init__(self, session: Session): self.session = session

    def add(self, entry: QueueEntry):
        model = QueueEntryModel(restaurant_id=entry.restaurant_id, name=entry.name, phone=entry.phone,
                                party_size=entry.party_size, status=entry.status.value,
                                created_at=entry.created_at, called_at=entry.called_at,
                                seated_at=entry.seated_at, cancelled_at=entry.cancelled_at)
        self.session.add(model); self.session.commit(); self.session.refresh(model)
        return to_entry(model)

    def get(self, entry_id: int):
        model = self.session.get(QueueEntryModel, entry_id)
        return to_entry(model) if model else None

    def list_waiting(self, restaurant_id: int):
        rows = self.session.scalars(select(QueueEntryModel).where(
            QueueEntryModel.restaurant_id == restaurant_id,
            QueueEntryModel.status == QueueStatus.WAITING.value).order_by(
            QueueEntryModel.created_at.asc(), QueueEntryModel.id.asc())).all()
        return [to_entry(row) for row in rows]

    def list_active(self, restaurant_id: int):
        rows = self.session.scalars(select(QueueEntryModel).where(
            QueueEntryModel.restaurant_id == restaurant_id,
            QueueEntryModel.status.in_([QueueStatus.WAITING.value, QueueStatus.CALLED.value])).order_by(
            QueueEntryModel.created_at.asc(), QueueEntryModel.id.asc())).all()
        return [to_entry(row) for row in rows]

    def position(self, entry: QueueEntry):
        if entry.status != QueueStatus.WAITING: return None
        return sum(1 for item in self.list_waiting(entry.restaurant_id)
                   if (item.created_at, item.id or 0) <= (entry.created_at, entry.id or 0))

    def call_next(self, restaurant_id: int, called_at: datetime):
        # SQLite has no row-locking equivalent. Serialize local claimers and retain
        # the conditional UPDATE so a stale selection cannot claim a called entry.
        with _call_next_lock:
            model = self.session.scalar(select(QueueEntryModel).where(
                QueueEntryModel.restaurant_id == restaurant_id,
                QueueEntryModel.status == QueueStatus.WAITING.value).order_by(
                QueueEntryModel.created_at.asc(), QueueEntryModel.id.asc()).limit(1))
            if model is None: return None
            result = self.session.execute(update(QueueEntryModel).where(
                QueueEntryModel.id == model.id,
                QueueEntryModel.status == QueueStatus.WAITING.value).values(
                    status=QueueStatus.CALLED.value, called_at=called_at))
            if result.rowcount != 1:
                self.session.rollback(); return None
            self.session.commit(); self.session.refresh(model)
            return to_entry(model)

    def transition(self, entry_id: int, expected: QueueStatus, new_status: QueueStatus, at: datetime):
        values = {"status": new_status.value}
        if new_status == QueueStatus.SEATED: values["seated_at"] = at
        elif new_status in (QueueStatus.CANCELLED, QueueStatus.NO_SHOW): values["cancelled_at"] = at
        result = self.session.execute(update(QueueEntryModel).where(
            QueueEntryModel.id == entry_id, QueueEntryModel.status == expected.value).values(**values))
        if result.rowcount != 1:
            self.session.rollback(); return None
        self.session.commit()
        return self.get(entry_id)

    def entries_between(self, restaurant_id: int, start: datetime, end: datetime):
        # SQLite stores UTC datetimes without timezone metadata. Comparing against
        # UTC bounds keeps the query portable; MySQL can use the same UTC bounds.
        rows = self.session.scalars(select(QueueEntryModel).where(
            QueueEntryModel.restaurant_id == restaurant_id,
            QueueEntryModel.created_at >= start.replace(tzinfo=None),
            QueueEntryModel.created_at < end.replace(tzinfo=None))).all()
        return [to_entry(row) for row in rows]
