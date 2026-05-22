from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OwnerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    login_id: str = Field(min_length=4, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("name must not be blank")

        return normalized_value

    @field_validator("login_id")
    @classmethod
    def validate_login_id(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("login_id must not be blank")

        return normalized_value


class OwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_id: UUID
    name: str
    login_id: str


class OwnerDogSummary(BaseModel):
    dog_id: UUID
    name: str
    birthday: date
    role: str | None


class OwnerDogsResponse(BaseModel):
    owner_id: UUID
    owner_name: str
    dogs: list[OwnerDogSummary]
