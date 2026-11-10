from __future__ import annotations

from datetime import date as Date
from datetime import datetime
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
    distance_km: Decimal | None = Field(
        default=None,
        ge=0,
        le=10,
        decimal_places=1,
        description="散歩した距離（km）",
        examples=[2.5],
    )
    duration_minutes: int | None = Field(
        default=None,
        ge=0,
        le=1439,
        description="散歩した時間（分）",
        examples=[30],
    )


class FoodEventDetail(EventDetailBase):
    menu: str | None = Field(
        default=None,
        description="与えたご飯の内容",
        examples=["ドライフード"],
    )
    amount_grams: int | None = Field(
        default=None,
        ge=0,
        le=1000,
        description="与えたご飯の量（g）",
        examples=[80],
    )

    @field_validator("menu", mode="before")
    @classmethod
    def validate_menu(cls, value: str | None) -> str | None:
        return TextEventDetailBase.validate_optional_text(value)


class ToiletEventDetail(TextEventDetailBase):
    type: str | None = Field(default=None, description="排泄の種類", examples=["pee"])
    condition: str | None = Field(default=None, description="排泄の状態", examples=["normal"])


EVENT_DETAIL_SCHEMAS = {
    "walk": WalkEventDetail,
    "food": FoodEventDetail,
    "toilet": ToiletEventDetail,
}


class EventCreateRequest(BaseModel):
    dog_id: UUID = Field(description="イベントを記録する犬のID")
    event_type_code: EventTypeCode = Field(
        description="イベント種別。walkは散歩、foodはご飯、toiletはトイレ",
        examples=["walk"],
    )
    occurred_at: datetime = Field(
        description="イベントが発生した日時。timezoneを含むISO 8601形式",
        examples=["2026-06-27T21:00:00+09:00"],
    )
    memo: str | None = Field(
        default=None,
        max_length=1000,
        description="イベントについての任意メモ",
        examples=["夕方の散歩"],
    )
    detail: dict[str, EventDetailValue] = Field(
        default_factory=dict,
        description="イベント種別ごとの詳細項目",
        examples=[{"distance_km": 2.5, "duration_minutes": 30}],
    )

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
    dog_id: UUID = Field(description="履歴を取得する犬のID")
    period: EventPeriod = Field(
        description="取得期間の単位。dayは日、weekは月曜始まりの週、monthは月",
        examples=["week"],
    )
    date: Date = Field(description="取得期間の基準日", examples=["2026-06-27"])
    event_type_code: EventTypeCode | None = Field(
        default=None,
        description="絞り込むイベント種別。省略時は全種別",
        examples=["walk"],
    )


class EventTypeResponse(BaseModel):
    event_type_id: UUID = Field(description="イベント種別のID")
    code: EventTypeCode = Field(description="イベント種別コード", examples=["walk"])
    display_name: str = Field(description="イベント種別の表示名", examples=["散歩"])


class EventResponse(BaseModel):
    event_id: UUID = Field(description="イベントのID")
    dog_id: UUID = Field(description="イベントを記録した犬のID")
    event_type: EventTypeResponse = Field(description="イベント種別")
    occurred_at: datetime = Field(description="イベントが発生した日時")
    memo: str | None = Field(
        description="イベントについての任意メモ",
        examples=["夕方の散歩"],
    )
    detail: dict[str, EventDetailValue] = Field(
        description="イベント種別ごとの詳細項目",
        examples=[{"distance_km": 2.5, "duration_minutes": 30}],
    )

    @field_serializer("detail")
    def serialize_detail(self, detail: dict[str, EventDetailValue]) -> dict[str, str | int | float | None]:
        return {
            key: float(value) if isinstance(value, Decimal) else value
            for key, value in detail.items()
        }


class EventCreateResponse(EventResponse):
    pass


class EventListResponse(BaseModel):
    events: list[EventResponse] = Field(description="指定期間に該当するイベントの一覧")
