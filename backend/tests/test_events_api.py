from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.models import Dog, Event, EventType, FoodEvent, ToiletEvent, WalkEvent
from app.routers.events import get_event_db_session


class FakeEventTypeResult:
    def __init__(self, event_type: EventType | None) -> None:
        self.event_type = event_type

    def scalar_one_or_none(self) -> EventType | None:
        return self.event_type


class FakeSession:
    def __init__(self) -> None:
        self.dogs: dict[UUID, Dog] = {}
        self.event_types: dict[str, EventType] = {}
        self.events: list[Event] = []
        self.walk_events: list[WalkEvent] = []
        self.food_events: list[FoodEvent] = []
        self.toilet_events: list[ToiletEvent] = []
        self.flushed = False
        self.committed = False
        self.refreshed = False
        self.rolled_back = False

    def add(self, item: Event | WalkEvent | FoodEvent | ToiletEvent) -> None:
        if isinstance(item, Event):
            item.event_id = uuid4()
            self.events.append(item)
            return

        if isinstance(item, WalkEvent):
            self.walk_events.append(item)
            return

        if isinstance(item, FoodEvent):
            self.food_events.append(item)
            return

        if isinstance(item, ToiletEvent):
            self.toilet_events.append(item)

    def get(self, model: type[Dog], item_id: UUID) -> Dog | None:
        if model is Dog:
            return self.dogs.get(item_id)

        return None

    def execute(self, statement):  # type: ignore[no-untyped-def]
        code = next(
            clause.right.value
            for clause in statement.whereclause.clauses
            if str(clause.left) == "event_types.code"
        )
        event_type = self.event_types.get(code)
        if event_type is not None and not event_type.is_active:
            event_type = None
        return FakeEventTypeResult(event_type)

    def flush(self) -> None:
        self.flushed = True

    def commit(self) -> None:
        self.committed = True

    def refresh(self, item: Event) -> None:
        self.refreshed = True

    def rollback(self) -> None:
        self.rolled_back = True


client = TestClient(app)


def create_fake_session() -> tuple[FakeSession, UUID]:
    fake_session = FakeSession()
    dog_id = UUID("00000000-0000-0000-0000-000000000010")
    fake_session.dogs[dog_id] = Dog(dog_id=dog_id, name="Pochi")
    fake_session.event_types["walk"] = EventType(
        event_type_id=UUID("00000000-0000-0000-0000-000000000101"),
        code="walk",
        display_name="散歩",
        is_active=True,
    )
    fake_session.event_types["food"] = EventType(
        event_type_id=UUID("00000000-0000-0000-0000-000000000102"),
        code="food",
        display_name="ご飯",
        is_active=True,
    )
    fake_session.event_types["toilet"] = EventType(
        event_type_id=UUID("00000000-0000-0000-0000-000000000103"),
        code="toilet",
        display_name="トイレ",
        is_active=True,
    )
    return fake_session, dog_id


def test_create_walk_event_creates_event_and_detail() -> None:
    fake_session, dog_id = create_fake_session()
    app.dependency_overrides[get_event_db_session] = lambda: fake_session

    response = client.post(
        "/events",
        json={
            "dog_id": str(dog_id),
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "memo": "  evening walk  ",
            "detail": {
                "distance": "  2km  ",
                "time": "  30min  ",
            },
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert fake_session.flushed is True
    assert fake_session.committed is True
    assert fake_session.refreshed is True
    assert len(fake_session.events) == 1
    assert len(fake_session.walk_events) == 1
    assert fake_session.events[0].dog_id == dog_id
    assert fake_session.events[0].event_type_id == fake_session.event_types["walk"].event_type_id
    assert fake_session.events[0].occurred_at == datetime.fromisoformat("2026-06-27T21:00:00+09:00")
    assert fake_session.events[0].memo == "evening walk"
    assert fake_session.walk_events[0].event_id == fake_session.events[0].event_id
    assert fake_session.walk_events[0].distance == "2km"
    assert fake_session.walk_events[0].time == "30min"
    assert response.json() == {
        "event_id": str(fake_session.events[0].event_id),
        "dog_id": str(dog_id),
        "event_type": {
            "event_type_id": str(fake_session.event_types["walk"].event_type_id),
            "code": "walk",
            "display_name": "散歩",
        },
        "occurred_at": "2026-06-27T21:00:00+09:00",
        "memo": "evening walk",
        "detail": {
            "distance": "2km",
            "time": "30min",
        },
    }


def test_create_food_event_creates_food_detail() -> None:
    fake_session, dog_id = create_fake_session()
    app.dependency_overrides[get_event_db_session] = lambda: fake_session

    response = client.post(
        "/events",
        json={
            "dog_id": str(dog_id),
            "event_type_code": "food",
            "occurred_at": "2026-06-27T08:00:00+09:00",
            "detail": {
                "menu": "meat",
                "amount": "80g",
            },
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert len(fake_session.food_events) == 1
    assert fake_session.food_events[0].menu == "meat"
    assert fake_session.food_events[0].amount == "80g"
    assert response.json()["event_type"]["code"] == "food"
    assert response.json()["detail"] == {"menu": "meat", "amount": "80g"}


def test_create_toilet_event_creates_toilet_detail() -> None:
    fake_session, dog_id = create_fake_session()
    app.dependency_overrides[get_event_db_session] = lambda: fake_session

    response = client.post(
        "/events",
        json={
            "dog_id": str(dog_id),
            "event_type_code": "toilet",
            "occurred_at": "2026-06-27T09:00:00+09:00",
            "detail": {
                "type": "pee",
                "condition": "normal",
            },
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert len(fake_session.toilet_events) == 1
    assert fake_session.toilet_events[0].type == "pee"
    assert fake_session.toilet_events[0].condition == "normal"
    assert response.json()["event_type"]["code"] == "toilet"
    assert response.json()["detail"] == {"type": "pee", "condition": "normal"}


def test_create_event_returns_not_found_when_dog_missing() -> None:
    fake_session, _ = create_fake_session()
    app.dependency_overrides[get_event_db_session] = lambda: fake_session

    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000099",
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {},
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "犬が見つかりません"}
    assert fake_session.committed is False
    assert fake_session.events == []


def test_create_event_returns_not_found_when_event_type_is_inactive() -> None:
    fake_session, dog_id = create_fake_session()
    fake_session.event_types["walk"].is_active = False
    app.dependency_overrides[get_event_db_session] = lambda: fake_session

    response = client.post(
        "/events",
        json={
            "dog_id": str(dog_id),
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {},
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "イベント種別が見つかりません"}
    assert fake_session.committed is False
    assert fake_session.events == []


def test_create_event_rejects_invalid_event_type_code() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "medicine",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {},
        },
    )

    assert response.status_code == 422


def test_create_event_rejects_detail_for_other_event_type() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {
                "menu": "meat",
            },
        },
    )

    assert response.status_code == 422
