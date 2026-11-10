from __future__ import annotations
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from datetime import date
from uuid import UUID
from app.schemas.common_params import (
    DOGNAME_MAX_LENGTH,
    DOGNAME_MIN_LENGTH,
    LOGINID_MAX_LENGTH,
    LOGINID_MIN_LENGTH,
)

DogGender = Literal["male", "female", "unknown"]


class DogCreateRequest(BaseModel):
    owner_id: UUID = Field(description="犬を紐づける飼い主のID")
    name: str = Field(
        min_length=DOGNAME_MIN_LENGTH,
        max_length=DOGNAME_MAX_LENGTH,
        description="犬の名前",
        examples=["ポチ"],
    )
    birthday: date | None = Field(
        default=None,
        description="犬の誕生日",
        examples=["2020-01-01"],
    )
    gender: DogGender | None = Field(default=None, description="犬の性別", examples=["male"])

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
    dog_id: UUID = Field(description="登録した犬のID")
    owner_id: UUID = Field(description="犬を紐づけた飼い主のID")
    name: str = Field(description="犬の名前", examples=["ポチ"])
    birthday: date | None = Field(description="犬の誕生日", examples=["2020-01-01"])
    gender: DogGender | None = Field(description="犬の性別", examples=["male"])


class DogOwnerAddRequest(BaseModel):
    login_id: str = Field(
        min_length=LOGINID_MIN_LENGTH,
        max_length=LOGINID_MAX_LENGTH,
        description="犬に追加する飼い主のログインID",
        examples=["taro"],
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


class DogIdName(BaseModel):
    dog_id: UUID = Field(description="犬のID")
    name: str = Field(description="犬の名前", examples=["ポチ"])


class OwnerIdName(BaseModel):
    owner_id: UUID = Field(description="飼い主のID")
    name: str = Field(description="飼い主の表示名", examples=["太郎"])


class DogOwnerAddResponse(BaseModel):
    dog: DogIdName = Field(description="紐づけ対象の犬")
    owner: OwnerIdName = Field(description="犬に追加した飼い主")


class DogUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=DOGNAME_MIN_LENGTH,
        max_length=DOGNAME_MAX_LENGTH,
        description="変更後の犬の名前",
        examples=["ハチ"],
    )
    birthday: date | None = Field(
        default=None,
        description="変更後の誕生日",
        examples=["2021-02-03"],
    )
    gender: DogGender | None = Field(default=None, description="変更後の性別", examples=["female"])

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

    dog_id: UUID = Field(description="犬のID")
    name: str = Field(description="犬の名前", examples=["ポチ"])
    birthday: date | None = Field(description="犬の誕生日", examples=["2020-01-01"])
    gender: DogGender | None = Field(description="犬の性別", examples=["male"])


class DogOwnerSummary(BaseModel):
    owner_id: UUID = Field(description="飼い主のID")
    name: str = Field(description="飼い主の表示名", examples=["花子"])
    role: str | None = Field(description="犬に対する飼い主の役割", examples=["primary"])


class DogOwnersResponse(BaseModel):
    dog_id: UUID = Field(description="犬のID")
    dog_name: str = Field(description="犬の名前", examples=["ポチ"])
    birthday: date | None = Field(description="犬の誕生日", examples=["2020-01-01"])
    gender: DogGender | None = Field(description="犬の性別", examples=["male"])
    owners: list[DogOwnerSummary] = Field(description="犬に紐づく飼い主の一覧")
