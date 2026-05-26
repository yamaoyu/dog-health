from __future__ import annotations

from uuid import UUID
from app.schemas.common_params import LOGINID_MIN_LENGTH, LOGINID_MAX_LENGTH
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    login_id: str = Field(min_length=LOGINID_MIN_LENGTH, max_length=LOGINID_MAX_LENGTH)

    @field_validator("login_id", mode="before")
    @classmethod
    def validate_login_id(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("ログインIDは文字列で入力してください")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("ログインIDは必須です")

        return normalized_value


class LoginResponse(BaseModel):
    owner_id: UUID
    name: str
    login_id: str
