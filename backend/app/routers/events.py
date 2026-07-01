from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.database import get_db_session
from app.repositories.events import CreatedEvent, EventDogNotFoundError, EventRepository, EventTypeNotFoundError, ListedEvent
from app.schemas.events import EventCreateRequest, EventCreateResponse, EventListQuery, EventListResponse, EventResponse, EventTypeResponse


router = APIRouter(prefix="/events", tags=["events"])


def get_event_db_session() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_event_repository() -> EventRepository:
    return EventRepository()


def get_event_period_bounds(query: EventListQuery, settings: Settings) -> tuple[datetime, datetime]:
    timezone = ZoneInfo(settings.app_timezone)
    start_at = datetime.combine(query.date, time.min, tzinfo=timezone)

    if query.period == "day":
        return start_at, start_at + timedelta(days=1)

    if query.period == "week":
        week_start = start_at - timedelta(days=start_at.weekday())
        return week_start, week_start + timedelta(days=7)

    if query.date.month == 12:
        next_month = query.date.replace(year=query.date.year + 1, month=1, day=1)
    else:
        next_month = query.date.replace(month=query.date.month + 1, day=1)

    month_start = query.date.replace(day=1)
    return (
        datetime.combine(month_start, time.min, tzinfo=timezone),
        datetime.combine(next_month, time.min, tzinfo=timezone),
    )


def to_event_response(listed_event: CreatedEvent | ListedEvent) -> EventResponse:
    return EventResponse(
        event_id=listed_event.event.event_id,
        dog_id=listed_event.event.dog_id,
        event_type=EventTypeResponse(
            event_type_id=listed_event.event_type.event_type_id,
            code=listed_event.event_type_code,
            display_name=listed_event.event_type.display_name,
        ),
        occurred_at=listed_event.event.occurred_at,
        memo=listed_event.event.memo,
        detail=listed_event.detail,
    )


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

    return EventCreateResponse(**to_event_response(created_event).model_dump())


@router.get("", response_model=EventListResponse)
def list_events(
    query: EventListQuery = Depends(),
    db_session: Session = Depends(get_event_db_session),
    event_repository: EventRepository = Depends(get_event_repository),
    settings: Settings = Depends(get_settings),
) -> EventListResponse:
    start_at, end_at = get_event_period_bounds(query, settings)

    try:
        events = event_repository.get_events_list(
            db_session=db_session,
            dog_id=query.dog_id,
            start_at=start_at,
            end_at=end_at,
            event_type_code=query.event_type_code,
        )
    except EventDogNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="犬が見つかりません",
        ) from None

    return EventListResponse(events=[to_event_response(event) for event in events])
