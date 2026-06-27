from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


EventTypeCode = Literal["walk", "food", "toilet"]


class EventDetailBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    distance: str | None = None
    time: str | None = None


class FoodEventDetail(EventDetailBase):
    menu: str | None = None
    amount: str | None = None


class ToiletEventDetail(EventDetailBase):
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
    detail: dict[str, str | None] = Field(default_factory=dict)

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


class EventTypeResponse(BaseModel):
    event_type_id: UUID
    code: EventTypeCode
    display_name: str


class EventCreateResponse(BaseModel):
    event_id: UUID
    dog_id: UUID
    event_type: EventTypeResponse
    occurred_at: datetime
    memo: str | None
    detail: dict[str, str | None]
