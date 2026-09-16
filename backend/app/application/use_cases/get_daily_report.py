from datetime import date, datetime, time, timedelta, timezone
from statistics import mean
from zoneinfo import ZoneInfo

from app.application.exceptions import NotFoundError


class GetDailyReport:
    def __init__(self, restaurants, queue): self.restaurants, self.queue = restaurants, queue

    def execute(self, restaurant_id: int, day: date):
        restaurant = self.restaurants.get(restaurant_id)
        if restaurant is None: raise NotFoundError("Restaurant not found")
        zone = ZoneInfo(restaurant.timezone)
        start_local = datetime.combine(day, time.min, tzinfo=zone)
        end_local = datetime.combine(day, time.min, tzinfo=zone) + timedelta(days=1)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)
        entries = self.queue.entries_between(restaurant_id, start_utc, end_utc)
        waits = []
        for e in entries:
            if e.status.value == "SEATED" and e.seated_at:
                created = e.created_at.replace(tzinfo=timezone.utc) if e.created_at.tzinfo is None else e.created_at
                seated = e.seated_at.replace(tzinfo=timezone.utc) if e.seated_at.tzinfo is None else e.seated_at
                waits.append((seated - created).total_seconds() / 60)
        return {"restaurant_id": restaurant.id, "restaurant_name": restaurant.name, "date": day,
                "joined_count": len(entries), "seated_count": sum(e.status.value == "SEATED" for e in entries),
                "cancelled_count": sum(e.status.value == "CANCELLED" for e in entries),
                "no_show_count": sum(e.status.value == "NO_SHOW" for e in entries),
                "average_wait_minutes": round(mean(waits), 2) if waits else None}
