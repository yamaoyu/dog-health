from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.repositories.events import EventDogNotFoundError, EventRepository, EventTypeNotFoundError
from app.schemas.events import EventCreateRequest, EventCreateResponse, EventTypeResponse


router = APIRouter(prefix="/events", tags=["events"])


def get_event_db_session() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_event_repository() -> EventRepository:
    return EventRepository()


@router.post("", response_model=EventCreateResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreateRequest,
    db_session: Session = Depends(get_event_db_session),
    event_repository: EventRepository = Depends(get_event_repository),
) -> EventCreateResponse:
    try:
        created_event = event_repository.create(db_session, payload)
    except EventDogNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="犬が見つかりません",
        ) from None
    except EventTypeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="イベント種別が見つかりません",
        ) from None

    return EventCreateResponse(
        event_id=created_event.event.event_id,
        dog_id=created_event.event.dog_id,
        event_type=EventTypeResponse(
            event_type_id=created_event.event_type.event_type_id,
            code=created_event.event_type_code,
            display_name=created_event.event_type.display_name,
        ),
        occurred_at=created_event.event.occurred_at,
        memo=created_event.event.memo,
        detail=created_event.detail,
    )
