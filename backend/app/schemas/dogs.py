from __future__ import annotations
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from datetime import date
from uuid import UUID
from app.schemas.common_params import DOGNAME_MIN_LENGTH, DOGNAME_MAX_LENGTH

DogGender = Literal["male", "female", "unknown"]


class DogCreateRequest(BaseModel):
    owner_id: UUID
    name: str = Field(min_length=DOGNAME_MIN_LENGTH, max_length=DOGNAME_MAX_LENGTH)
    birthday: date | None = None
    gender: DogGender | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("名前は文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("名前は必須です")

        return normalized_value


class DogCreateResponse(BaseModel):
    dog_id: UUID
    owner_id: UUID
    name: str
    birthday: date | None
    gender: DogGender | None


class DogOwnerAddRequest(BaseModel):
    owner_id: UUID


class DogIdName(BaseModel):
    dog_id: UUID
    name: str


class OwnerIdName(BaseModel):
    owner_id: UUID
    name: str


class DogOwnerAddResponse(BaseModel):
    dog: DogIdName
    owner: OwnerIdName


class DogUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=DOGNAME_MIN_LENGTH,
        max_length=DOGNAME_MAX_LENGTH,
    )
    birthday: date | None = None
    gender: DogGender | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("名前は文字列で入力してください")

        if not isinstance(value, str):
            raise ValueError("名前は文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("名前は必須です")

        return normalized_value

    @model_validator(mode="after")
    def validate_update_fields(self) -> "DogUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("更新する項目を指定してください")
        return self


class DogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dog_id: UUID
    name: str
    birthday: date | None
    gender: DogGender | None


class DogOwnerSummary(BaseModel):
    owner_id: UUID
    name: str
    role: str | None


class DogOwnersResponse(BaseModel):
    dog_id: UUID
    dog_name: str
    birthday: date | None
    gender: DogGender | None
    owners: list[DogOwnerSummary]
