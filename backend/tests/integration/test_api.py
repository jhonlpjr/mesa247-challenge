from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import QueueEntryModel, RestaurantModel
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.sqlalchemy_queue_repository import SQLAlchemyQueueRepository
from app.main import app


def test_queue_api_and_persistence():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        db.add(RestaurantModel(id=1, name="Demo", created_at=datetime.now(timezone.utc))); db.commit()
    app.dependency_overrides[get_db] = lambda: Session()
    try:
        client = TestClient(app)
        created = client.post("/restaurants/1/queue", json={"name": "Ana", "phone": "999999999", "party_size": 2})
        assert created.status_code == 201
        entry_id = created.json()["id"]
        assert client.get("/restaurants/1/queue").json()["entries"][0]["position"] == 1
        called = client.post("/restaurants/1/queue/call-next")
        assert called.status_code == 200 and called.json()["status"] == "CALLED"
        assert called.json()["called_at"] is not None
        assert client.get(f"/queue/{entry_id}").json()["position"] is None
        assert client.post("/restaurants/1/queue/call-next").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_concurrent_call_next_claims_entry_once(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'concurrency.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        db.add(RestaurantModel(id=1, name="Demo", created_at=datetime.now(timezone.utc)))
        db.add(QueueEntryModel(restaurant_id=1, name="Ana", phone="999999999", party_size=2,
                               status="WAITING", created_at=datetime.now(timezone.utc)))
        db.commit()

    def claim():
        with Session() as db:
            return SQLAlchemyQueueRepository(db).call_next(1, datetime.now(timezone.utc))

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: claim(), range(2)))
    assert sum(result is not None for result in results) == 1
