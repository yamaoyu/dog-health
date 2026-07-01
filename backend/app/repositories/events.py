from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Dog, Event, EventType, FoodEvent, ToiletEvent, WalkEvent
from app.schemas.events import EventCreateRequest, EventDetailValue, EventTypeCode


class EventDogNotFoundError(Exception):
    pass


class EventTypeNotFoundError(Exception):
    pass


class DetailRepository(Protocol):
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, EventDetailValue]) -> None:
        pass


class WalkEventRepository:
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, EventDetailValue]) -> None:
        db_session.add(
            WalkEvent(
                event_id=event_id,
                distance_km=detail.get("distance_km"),
                duration_minutes=detail.get("duration_minutes"),
            ),
        )


class FoodEventRepository:
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, EventDetailValue]) -> None:
        db_session.add(
            FoodEvent(
                event_id=event_id,
                menu=detail.get("menu"),
                amount_grams=detail.get("amount_grams"),
            ),
        )


class ToiletEventRepository:
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, EventDetailValue]) -> None:
        db_session.add(
            ToiletEvent(
                event_id=event_id,
                type=detail.get("type"),
                condition=detail.get("condition"),
            ),
        )


EVENT_DETAIL_REPOSITORIES: dict[str, DetailRepository] = {
    "walk": WalkEventRepository(),
    "food": FoodEventRepository(),
    "toilet": ToiletEventRepository(),
}


@dataclass(frozen=True)
class CreatedEvent:
    event: Event
    event_type: EventType
    event_type_code: EventTypeCode
    detail: dict[str, EventDetailValue]


@dataclass(frozen=True)
class ListedEvent:
    event: Event
    event_type: EventType
    event_type_code: EventTypeCode
    detail: dict[str, EventDetailValue]


def build_event_detail(event: Event) -> dict[str, EventDetailValue]:
    event_type_code = event.event_type.code

    if event_type_code == "walk":
        walk_event = event.walk_event
        return {
            "distance_km": walk_event.distance_km if walk_event is not None else None,
            "duration_minutes": walk_event.duration_minutes if walk_event is not None else None,
        }

    if event_type_code == "food":
        food_event = event.food_event
        return {
            "menu": food_event.menu if food_event is not None else None,
            "amount_grams": food_event.amount_grams if food_event is not None else None,
        }

    toilet_event = event.toilet_event
    return {
        "type": toilet_event.type if toilet_event is not None else None,
        "condition": toilet_event.condition if toilet_event is not None else None,
    }


class EventRepository:
    def create(self, db_session: Session, payload: EventCreateRequest) -> CreatedEvent:
        dog = db_session.get(Dog, payload.dog_id)
        if dog is None:
            raise EventDogNotFoundError

        event_type = db_session.execute(
            select(EventType).where(
                EventType.code == payload.event_type_code,
                EventType.is_active.is_(True),
            ),
        ).scalar_one_or_none()
        if event_type is None:
            raise EventTypeNotFoundError

        try:
            event = Event(
                dog_id=dog.dog_id,
                event_type_id=event_type.event_type_id,
                occurred_at=payload.occurred_at,
                memo=payload.memo,
            )
            db_session.add(event)
            db_session.flush()

            detail_repository = EVENT_DETAIL_REPOSITORIES[payload.event_type_code]
            detail_repository.create(db_session, event.event_id, payload.detail)

            db_session.commit()
            db_session.refresh(event)
        except Exception:
            db_session.rollback()
            raise

        return CreatedEvent(
            event=event,
            event_type=event_type,
            event_type_code=payload.event_type_code,
            detail=payload.detail,
        )

    def get_events_list(
        self,
        db_session: Session,
        dog_id: UUID,
        start_at: datetime,
        end_at: datetime,
        event_type_code: EventTypeCode | None,
    ) -> list[ListedEvent]:
        dog = db_session.get(Dog, dog_id)
        if dog is None:
            raise EventDogNotFoundError

        statement = (
            select(Event)
            .options(
                joinedload(Event.event_type),
                joinedload(Event.walk_event),
                joinedload(Event.food_event),
                joinedload(Event.toilet_event),
            )
            .where(
                Event.dog_id == dog_id,
                Event.occurred_at >= start_at,
                Event.occurred_at < end_at,
            )
        )

        if event_type_code is not None:
            statement = statement.join(EventType).where(EventType.code == event_type_code)

        events = db_session.execute(
            statement.order_by(Event.occurred_at.asc(), Event.event_id.asc()),
        ).scalars().all()

        return [
            ListedEvent(
                event=event,
                event_type=event.event_type,
                event_type_code=event.event_type.code,
                detail=build_event_detail(event),
            )
            for event in events
        ]
