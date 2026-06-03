from __future__ import annotations

from datetime import date
from uuid import UUID

from app.schemas.common_params import (
    LOGINID_MAX_LENGTH,
    LOGINID_MIN_LENGTH,
    OWNERNAME_MAX_LENGTH,
    OWNERNAME_MIN_LENGTH,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OwnerCreateRequest(BaseModel):
    name: str = Field(min_length=OWNERNAME_MIN_LENGTH, max_length=OWNERNAME_MAX_LENGTH)
    login_id: str = Field(min_length=LOGINID_MIN_LENGTH, max_length=LOGINID_MAX_LENGTH)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("名前は文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("名前は必須です")
        return normalized_value

    @field_validator("login_id", mode="before")
    @classmethod
    def validate_login_id(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("ログインIDは文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("login_idは必須です")

        return normalized_value


class OwnerUpdateRequest(BaseModel):
    login_id: str | None = Field(
        default=None,
        min_length=LOGINID_MIN_LENGTH,
        max_length=LOGINID_MAX_LENGTH,
    )
    name: str | None = Field(
        default=None,
        min_length=OWNERNAME_MIN_LENGTH,
        max_length=OWNERNAME_MAX_LENGTH,
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        if not isinstance(value, str):
            raise ValueError("名前は文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("名前は必須です")
        return normalized_value

    @field_validator("login_id", mode="before")
    @classmethod
    def validate_login_id(cls, value: str | None) -> str:
        if not isinstance(value, str):
            raise ValueError("ログインIDは文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("login_idは必須です")

        return normalized_value

    @model_validator(mode="after")
    def validate_update_fields(self) -> "OwnerUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("更新する項目を指定してください")
        return self


class OwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_id: UUID
    name: str
    login_id: str


class OwnerDogSummary(BaseModel):
    dog_id: UUID
    name: str
    birthday: date


class OwnerDogsResponse(BaseModel):
    owner_id: UUID
    owner_name: str
    dogs: list[OwnerDogSummary]
