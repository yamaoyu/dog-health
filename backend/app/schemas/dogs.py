from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DogCreateRequest(BaseModel):
    owner_id: UUID
    name: str = Field(min_length=2, max_length=20)
    birthday: date
    role: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("name must not be blank")

        return normalized_value

    @field_validator("role")
    @classmethod
    def normalize_role(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()
        return normalized_value or None


class DogCreateResponse(BaseModel):
    dog_id: UUID
    owner_id: UUID
    name: str
    birthday: date
    role: str | None


class DogOwnerSummary(BaseModel):
    owner_id: UUID
    name: str
    role: str | None


class DogOwnersResponse(BaseModel):
    dog_id: UUID
    dog_name: str
    birthday: date
    owners: list[DogOwnerSummary]
