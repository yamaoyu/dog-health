from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Dog, Event, EventType, FoodEvent, ToiletEvent, WalkEvent
from app.schemas.events import EventCreateRequest, EventTypeCode


class EventDogNotFoundError(Exception):
    pass


class EventTypeNotFoundError(Exception):
    pass


class DetailRepository(Protocol):
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, str | None]) -> None:
        pass


class WalkEventRepository:
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, str | None]) -> None:
        db_session.add(
            WalkEvent(
                event_id=event_id,
                distance=detail.get("distance"),
                time=detail.get("time"),
            ),
        )


class FoodEventRepository:
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, str | None]) -> None:
        db_session.add(
            FoodEvent(
                event_id=event_id,
                menu=detail.get("menu"),
                amount=detail.get("amount"),
            ),
        )


class ToiletEventRepository:
    def create(self, db_session: Session, event_id: UUID, detail: dict[str, str | None]) -> None:
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
    detail: dict[str, str | None]


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
