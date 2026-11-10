from __future__ import annotations

from collections.abc import Generator
from datetime import date as Date
from datetime import datetime, time, timedelta
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.database import get_db_session
from app.repositories.events import (
    CreatedEvent,
    EventDogNotFoundError,
    EventRepository,
    EventTypeNotFoundError,
    ListedEvent,
)
from app.schemas.events import (
    EventCreateRequest,
    EventCreateResponse,
    EventListQuery,
    EventListResponse,
    EventPeriod,
    EventResponse,
    EventTypeCode,
    EventTypeResponse,
)


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


@router.post(
    "",
    response_model=EventCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="イベントを登録する",
    description="犬の散歩、ご飯、トイレのいずれかのイベントを登録します。",
    response_description="登録したイベントの情報",
    responses={404: {"description": "指定した犬または利用可能なイベント種別が存在しません。"}},
)
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


@router.get(
    "",
    response_model=EventListResponse,
    summary="イベント履歴を取得する",
    description=(
        "指定した犬のイベントを日・週・月の期間で取得します。"
        "週は月曜日始まりで、イベント種別による絞り込みもできます。"
    ),
    response_description="指定期間に該当するイベントの一覧",
    responses={404: {"description": "指定した犬が存在しません。"}},
)
def list_events(
    dog_id: Annotated[UUID, Query(description="履歴を取得する犬のID")],
    period: Annotated[
        EventPeriod,
        Query(
            description="取得期間の単位。dayは日、weekは月曜始まりの週、monthは月",
            examples=["week"],
        ),
    ],
    date: Annotated[
        Date,
        Query(description="取得期間の基準日", examples=["2026-06-27"]),
    ],
    event_type_code: Annotated[
        EventTypeCode | None,
        Query(description="絞り込むイベント種別。省略時は全種別", examples=["walk"]),
    ] = None,
    db_session: Session = Depends(get_event_db_session),
    event_repository: EventRepository = Depends(get_event_repository),
    settings: Settings = Depends(get_settings),
) -> EventListResponse:
    query = EventListQuery(
        dog_id=dog_id,
        period=period,
        date=date,
        event_type_code=event_type_code,
    )
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
