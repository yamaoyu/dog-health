from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    login_id: str = Field(min_length=4, max_length=20)

    @field_validator("login_id")
    @classmethod
    def validate_login_id(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("login_id must not be blank")

        return normalized_value


class LoginResponse(BaseModel):
    owner_id: UUID
    name: str
    login_id: str
