from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.models import Dog, Event, EventType, FoodEvent, ToiletEvent, WalkEvent
from app.repositories.events import EventDogNotFoundError, ListedEvent
from app.routers.events import get_event_db_session, get_event_repository


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


class FakeListEventRepository:
    def __init__(self, events: list[ListedEvent] | None = None, dog_missing: bool = False) -> None:
        self.events = events or []
        self.dog_missing = dog_missing
        self.calls: list[dict[str, object]] = []

    def get_events_list(
        self,
        db_session: FakeSession,
        dog_id: UUID,
        start_at: datetime,
        end_at: datetime,
        event_type_code: str | None,
    ) -> list[ListedEvent]:
        self.calls.append(
            {
                "dog_id": dog_id,
                "start_at": start_at,
                "end_at": end_at,
                "event_type_code": event_type_code,
            },
        )

        if self.dog_missing:
            raise EventDogNotFoundError

        return [
            event
            for event in self.events
            if event.event.dog_id == dog_id
            and start_at <= event.event.occurred_at < end_at
            and (event_type_code is None or event.event_type_code == event_type_code)
        ]


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


def create_listed_event_mock(
    *,
    event_id: UUID,
    dog_id: UUID,
    event_type: EventType,
    occurred_at: str,
    memo: str | None,
    detail: dict[str, str | int | Decimal | None],
) -> ListedEvent:
    event = Event(
        event_id=event_id,
        dog_id=dog_id,
        event_type_id=event_type.event_type_id,
        occurred_at=datetime.fromisoformat(occurred_at),
        memo=memo,
    )
    return ListedEvent(
        event=event,
        event_type=event_type,
        event_type_code=event_type.code,
        detail=detail,
    )


def create_event_types_mock() -> dict[str, EventType]:
    return {
        "walk": EventType(
            event_type_id=UUID("00000000-0000-0000-0000-000000000101"),
            code="walk",
            display_name="散歩",
            is_active=True,
        ),
        "food": EventType(
            event_type_id=UUID("00000000-0000-0000-0000-000000000102"),
            code="food",
            display_name="ご飯",
            is_active=True,
        ),
        "toilet": EventType(
            event_type_id=UUID("00000000-0000-0000-0000-000000000103"),
            code="toilet",
            display_name="トイレ",
            is_active=True,
        ),
    }


def override_event_settings() -> Settings:
    return Settings(
        app_name="dog-health-api",
        app_env="test",
        app_timezone="Asia/Tokyo",
        frontend_origins=("http://localhost:5180",),
        db_host="db",
        db_port=5432,
        db_name="dog_health",
        db_user="dog_health",
        db_password="dog_health_password",
    )


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
                "distance_km": 2.0,
                "duration_minutes": 90,
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
    assert fake_session.walk_events[0].distance_km == Decimal("2.0")
    assert fake_session.walk_events[0].duration_minutes == 90
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
            "distance_km": 2.0,
            "duration_minutes": 90,
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
                "amount_grams": 80,
            },
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert len(fake_session.food_events) == 1
    assert fake_session.food_events[0].menu == "meat"
    assert fake_session.food_events[0].amount_grams == 80
    assert response.json()["event_type"]["code"] == "food"
    assert response.json()["detail"] == {"menu": "meat", "amount_grams": 80}


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


def test_list_events_returns_month_events() -> None:
    '''
    2026年6月のイベントを取得する場合、2026年6月1日0時から2026年7月1日0時までのイベントが返されることを確認する
    イベントの順番は日付の古い順
    '''
    fake_session, dog_id = create_fake_session()
    event_types = create_event_types_mock()
    repository = FakeListEventRepository(
        [
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000201"),
                dog_id=dog_id,
                event_type=event_types["walk"],
                occurred_at="2026-06-01T09:00:00+09:00",
                memo="morning",
                detail={"distance_km": Decimal("1.5"), "duration_minutes": 30},
            ),
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000202"),
                dog_id=dog_id,
                event_type=event_types["food"],
                occurred_at="2026-06-15T08:00:00+09:00",
                memo=None,
                detail={"menu": "dry food", "amount_grams": 80},
            ),
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000203"),
                dog_id=dog_id,
                event_type=event_types["toilet"],
                occurred_at="2026-07-01T00:00:00+09:00",
                memo=None,
                detail={"type": "pee", "condition": "normal"},
            ),
        ],
    )
    app.dependency_overrides[get_event_db_session] = lambda: fake_session
    app.dependency_overrides[get_event_repository] = lambda: repository
    app.dependency_overrides[get_settings] = override_event_settings

    response = client.get(f"/events?dog_id={dog_id}&period=month&date=2026-06-20")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert repository.calls[0]["start_at"] == datetime.fromisoformat("2026-06-01T00:00:00+09:00")
    assert repository.calls[0]["end_at"] == datetime.fromisoformat("2026-07-01T00:00:00+09:00")
    assert response.json() == {
        "events": [
            {
                "event_id": "00000000-0000-0000-0000-000000000201",
                "dog_id": str(dog_id),
                "event_type": {
                    "event_type_id": str(event_types["walk"].event_type_id),
                    "code": "walk",
                    "display_name": "散歩",
                },
                "occurred_at": "2026-06-01T09:00:00+09:00",
                "memo": "morning",
                "detail": {"distance_km": 1.5, "duration_minutes": 30},
            },
            {
                "event_id": "00000000-0000-0000-0000-000000000202",
                "dog_id": str(dog_id),
                "event_type": {
                    "event_type_id": str(event_types["food"].event_type_id),
                    "code": "food",
                    "display_name": "ご飯",
                },
                "occurred_at": "2026-06-15T08:00:00+09:00",
                "memo": None,
                "detail": {"menu": "dry food", "amount_grams": 80},
            },
        ],
    }


def test_list_events_returns_month_events_filtered_by_category() -> None:
    '''
    2026年6月のイベントを取得する場合、2026年6月1日0時から2026年7月1日0時までのイベントが返されることを確認する
    イベントの順番は日付の古い順
    カテゴリでフィルタリングできることを確認する
    '''
    fake_session, dog_id = create_fake_session()
    event_types = create_event_types_mock()
    repository = FakeListEventRepository(
        [
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000201"),
                dog_id=dog_id,
                event_type=event_types["walk"],
                occurred_at="2026-06-01T09:00:00+09:00",
                memo="morning",
                detail={"distance_km": Decimal("1.5"), "duration_minutes": 30},
            ),
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000202"),
                dog_id=dog_id,
                event_type=event_types["food"],
                occurred_at="2026-06-15T08:00:00+09:00",
                memo=None,
                detail={"menu": "dry food", "amount_grams": 80},
            ),
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000203"),
                dog_id=dog_id,
                event_type=event_types["toilet"],
                occurred_at="2026-07-01T00:00:00+09:00",
                memo=None,
                detail={"type": "pee", "condition": "normal"},
            ),
        ],
    )
    app.dependency_overrides[get_event_db_session] = lambda: fake_session
    app.dependency_overrides[get_event_repository] = lambda: repository
    app.dependency_overrides[get_settings] = override_event_settings

    response = client.get(
        f"/events?dog_id={dog_id}&period=month&date=2026-06-20&event_type_code=walk")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert repository.calls[0]["start_at"] == datetime.fromisoformat("2026-06-01T00:00:00+09:00")
    assert repository.calls[0]["end_at"] == datetime.fromisoformat("2026-07-01T00:00:00+09:00")
    assert response.json() == {
        "events": [
            {
                "event_id": "00000000-0000-0000-0000-000000000201",
                "dog_id": str(dog_id),
                "event_type": {
                    "event_type_id": str(event_types["walk"].event_type_id),
                    "code": "walk",
                    "display_name": "散歩",
                },
                "occurred_at": "2026-06-01T09:00:00+09:00",
                "memo": "morning",
                "detail": {"distance_km": 1.5, "duration_minutes": 30},
            }
        ],
    }


def test_list_events_returns_week_events_filtered_by_category() -> None:
    '''
    週ごとのイベントを取得する場合は、指定された日付が含む週の月曜日から日曜日が範囲
    '''
    fake_session, dog_id = create_fake_session()
    event_types = create_event_types_mock()
    repository = FakeListEventRepository(
        [
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000211"),
                dog_id=dog_id,
                event_type=event_types["walk"],
                occurred_at="2026-06-29T00:00:00+09:00",
                memo=None,
                detail={"distance_km": Decimal("2.0"), "duration_minutes": 40},
            ),
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000212"),
                dog_id=dog_id,
                event_type=event_types["walk"],
                occurred_at="2026-07-06T00:00:00+09:00",
                memo=None,
                detail={"distance_km": Decimal("3.0"), "duration_minutes": 50},
            ),
        ],
    )
    app.dependency_overrides[get_event_db_session] = lambda: fake_session
    app.dependency_overrides[get_event_repository] = lambda: repository
    app.dependency_overrides[get_settings] = override_event_settings

    response = client.get(
        f"/events?dog_id={dog_id}&period=week&date=2026-07-03&event_type_code=walk")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert repository.calls[0]["start_at"] == datetime.fromisoformat("2026-06-29T00:00:00+09:00")
    assert repository.calls[0]["end_at"] == datetime.fromisoformat("2026-07-06T00:00:00+09:00")
    assert response.json() == {
        "events": [
            {
                "event_id": "00000000-0000-0000-0000-000000000211",
                "dog_id": str(dog_id),
                "event_type": {
                    "event_type_id": str(event_types["walk"].event_type_id),
                    "code": "walk",
                    "display_name": "散歩",
                },
                "occurred_at": "2026-06-29T00:00:00+09:00",
                "memo": None,
                "detail": {"distance_km": 2.0, "duration_minutes": 40},
            }
        ]
    }


def test_list_events_returns_day_events_filtered_by_category() -> None:
    '''
    特定日のイベントからカテゴリでフィルタリングして取得できる
    '''
    fake_session, dog_id = create_fake_session()
    event_types = create_event_types_mock()
    repository = FakeListEventRepository(
        [
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000221"),
                dog_id=dog_id,
                event_type=event_types["food"],
                occurred_at="2026-07-03T08:00:00+09:00",
                memo=None,
                detail={"menu": "dry food", "amount_grams": 80},
            ),
            create_listed_event_mock(
                event_id=UUID("00000000-0000-0000-0000-000000000222"),
                dog_id=dog_id,
                event_type=event_types["toilet"],
                occurred_at="2026-07-03T09:00:00+09:00",
                memo=None,
                detail={"type": "pee", "condition": "normal"},
            ),
        ],
    )
    app.dependency_overrides[get_event_db_session] = lambda: fake_session
    app.dependency_overrides[get_event_repository] = lambda: repository
    app.dependency_overrides[get_settings] = override_event_settings

    response = client.get(
        f"/events?dog_id={dog_id}&period=day&date=2026-07-03&event_type_code=food")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert repository.calls[0]["start_at"] == datetime.fromisoformat("2026-07-03T00:00:00+09:00")
    assert repository.calls[0]["end_at"] == datetime.fromisoformat("2026-07-04T00:00:00+09:00")
    assert repository.calls[0]["event_type_code"] == "food"
    assert response.json() == {
        "events": [
            {
                "event_id": "00000000-0000-0000-0000-000000000221",
                "dog_id": str(dog_id),
                "event_type": {
                    "event_type_id": str(event_types["food"].event_type_id),
                    "code": "food",
                    "display_name": "ご飯",
                },
                "occurred_at": "2026-07-03T08:00:00+09:00",
                "memo": None,
                "detail": {"menu": "dry food", "amount_grams": 80},
            },
        ]
    }


def test_list_events_returns_empty_events_when_period_has_no_events() -> None:
    fake_session, dog_id = create_fake_session()
    repository = FakeListEventRepository()
    app.dependency_overrides[get_event_db_session] = lambda: fake_session
    app.dependency_overrides[get_event_repository] = lambda: repository
    app.dependency_overrides[get_settings] = override_event_settings

    response = client.get(f"/events?dog_id={dog_id}&period=day&date=2026-07-03")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"events": []}


def test_list_events_returns_not_found_when_dog_missing() -> None:
    fake_session, dog_id = create_fake_session()
    repository = FakeListEventRepository(dog_missing=True)
    app.dependency_overrides[get_event_db_session] = lambda: fake_session
    app.dependency_overrides[get_event_repository] = lambda: repository
    app.dependency_overrides[get_settings] = override_event_settings

    response = client.get(f"/events?dog_id={dog_id}&period=day&date=2026-07-03")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "犬が見つかりません"}


def test_list_events_rejects_missing_period() -> None:
    response = client.get("/events?dog_id=00000000-0000-0000-0000-000000000010&date=2026-07-03")

    assert response.status_code == 422


def test_list_events_rejects_missing_date() -> None:
    response = client.get("/events?dog_id=00000000-0000-0000-0000-000000000010&period=day")

    assert response.status_code == 422


def test_list_events_rejects_invalid_period() -> None:
    response = client.get(
        "/events?dog_id=00000000-0000-0000-0000-000000000010&period=all&date=2026-07-03",
    )

    assert response.status_code == 422


def test_list_events_rejects_invalid_event_type_code() -> None:
    response = client.get(
        "/events?dog_id=00000000-0000-0000-0000-000000000010&period=day&date=2026-07-03&event_type_code=medicine",
    )

    assert response.status_code == 422


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


def test_create_food_event_rejects_amount_field() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "food",
            "occurred_at": "2026-06-27T08:00:00+09:00",
            "detail": {
                "menu": "meat",
                "amount": "80g",
            },
        },
    )

    assert response.status_code == 422


def test_create_food_event_rejects_negative_amount_grams() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "food",
            "occurred_at": "2026-06-27T08:00:00+09:00",
            "detail": {
                "menu": "meat",
                "amount_grams": -1,
            },
        },
    )

    assert response.status_code == 422


def test_create_food_event_rejects_amount_grams_over_limit() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "food",
            "occurred_at": "2026-06-27T08:00:00+09:00",
            "detail": {
                "menu": "meat",
                "amount_grams": 1001,
            },
        },
    )

    assert response.status_code == 422


def test_create_walk_event_rejects_invalid_distance_range() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {
                "distance_km": 10.1,
                "duration_minutes": 30,
            },
        },
    )

    assert response.status_code == 422


def test_create_walk_event_rejects_distance_with_too_many_decimal_places() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {
                "distance_km": 2.05,
                "duration_minutes": 30,
            },
        },
    )

    assert response.status_code == 422


def test_create_walk_event_rejects_invalid_duration_range() -> None:
    response = client.post(
        "/events",
        json={
            "dog_id": "00000000-0000-0000-0000-000000000010",
            "event_type_code": "walk",
            "occurred_at": "2026-06-27T21:00:00+09:00",
            "detail": {
                "distance_km": 2.0,
                "duration_minutes": 1440,
            },
        },
    )

    assert response.status_code == 422
