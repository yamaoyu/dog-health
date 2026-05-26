from __future__ import annotations
from pydantic import BaseModel, Field, field_validator

from datetime import date
from uuid import UUID
from app.schemas.common_params import DOGNAME_MIN_LENGTH, DOGNAME_MAX_LENGTH


class DogCreateRequest(BaseModel):
    owner_id: UUID
    name: str = Field(min_length=DOGNAME_MIN_LENGTH, max_length=DOGNAME_MAX_LENGTH)
    birthday: date

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("名前は必須です")

        return normalized_value


class DogCreateResponse(BaseModel):
    dog_id: UUID
    owner_id: UUID
    name: str
    birthday: date


class DogOwnerSummary(BaseModel):
    owner_id: UUID
    name: str
    role: str | None


class DogOwnersResponse(BaseModel):
    dog_id: UUID
    dog_name: str
    birthday: date
    owners: list[DogOwnerSummary]
