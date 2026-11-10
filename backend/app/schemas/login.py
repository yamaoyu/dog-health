from __future__ import annotations

from uuid import UUID
from app.schemas.common_params import LOGINID_MIN_LENGTH, LOGINID_MAX_LENGTH
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    login_id: str = Field(
        min_length=LOGINID_MIN_LENGTH,
        max_length=LOGINID_MAX_LENGTH,
        description="飼い主が登録したログインID",
        examples=["hanako"],
    )

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
    owner_id: UUID = Field(description="ログインした飼い主のID")
    name: str = Field(description="飼い主の表示名", examples=["花子"])
    login_id: str = Field(description="飼い主のログインID", examples=["hanako"])
