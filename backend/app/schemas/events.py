from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator


EventTypeCode = Literal["walk", "food", "toilet"]
EventPeriod = Literal["day", "week", "month"]
EventDetailValue = str | int | Decimal | None


class EventDetailBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TextEventDetailBase(EventDetailBase):
    @field_validator("*", mode="before")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("詳細は文字列で入力してください")

        normalized_value = value.strip()
        return normalized_value or None


class WalkEventDetail(EventDetailBase):
    distance_km: Decimal | None = Field(default=None, ge=0, le=10, decimal_places=1)
    duration_minutes: int | None = Field(default=None, ge=0, le=1439)


class FoodEventDetail(EventDetailBase):
    menu: str | None = None
    amount_grams: int | None = Field(default=None, ge=0, le=1000)

    @field_validator("menu", mode="before")
    @classmethod
    def validate_menu(cls, value: str | None) -> str | None:
        return TextEventDetailBase.validate_optional_text(value)


class ToiletEventDetail(TextEventDetailBase):
    type: str | None = None
    condition: str | None = None


EVENT_DETAIL_SCHEMAS = {
    "walk": WalkEventDetail,
    "food": FoodEventDetail,
    "toilet": ToiletEventDetail,
}


class EventCreateRequest(BaseModel):
    dog_id: UUID
    event_type_code: EventTypeCode
    occurred_at: datetime
    memo: str | None = Field(default=None, max_length=1000)
    detail: dict[str, EventDetailValue] = Field(default_factory=dict)

    @field_validator("memo", mode="before")
    @classmethod
    def validate_memo(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("メモは文字列で入力してください")

        normalized_value = value.strip()
        return normalized_value or None

    @model_validator(mode="after")
    def validate_detail(self) -> "EventCreateRequest":
        schema = EVENT_DETAIL_SCHEMAS[self.event_type_code]
        self.detail = schema.model_validate(self.detail).model_dump()
        return self


class EventListQuery(BaseModel):
    dog_id: UUID
    period: EventPeriod
    date: date
    event_type_code: EventTypeCode | None = None


class EventTypeResponse(BaseModel):
    event_type_id: UUID
    code: EventTypeCode
    display_name: str


class EventResponse(BaseModel):
    event_id: UUID
    dog_id: UUID
    event_type: EventTypeResponse
    occurred_at: datetime
    memo: str | None
    detail: dict[str, EventDetailValue]

    @field_serializer("detail")
    def serialize_detail(self, detail: dict[str, EventDetailValue]) -> dict[str, str | int | float | None]:
        return {
            key: float(value) if isinstance(value, Decimal) else value
            for key, value in detail.items()
        }


class EventCreateResponse(EventResponse):
    pass


class EventListResponse(BaseModel):
    events: list[EventResponse]
