from __future__ import annotations

from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.entities import Dog, Owner, OwnerDog
from app.schemas.dogs import (
    DogCreateRequest,
    DogCreateResponse,
    DogIdName,
    DogOwnerAddRequest,
    DogOwnerAddResponse,
    DogOwnerSummary,
    DogOwnersResponse,
    DogResponse,
    DogUpdateRequest,
    OwnerIdName,
)


router = APIRouter(prefix="/dogs", tags=["dogs"])

DogIdPath = Annotated[
    UUID,
    Path(
        description="対象となる犬のID",
        examples=["00000000-0000-0000-0000-000000000010"],
    ),
]


def get_dog_db_session() -> Generator[Session, None, None]:
    yield from get_db_session()


@router.post(
    "",
    response_model=DogCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="犬を登録する",
    description="犬を登録し、指定した飼い主に紐づけます。",
    response_description="登録した犬と飼い主のID",
    responses={404: {"description": "指定した飼い主が存在しません。"}},
)
def create_dog(
    payload: DogCreateRequest,
    db_session: Session = Depends(get_dog_db_session),
) -> DogCreateResponse:
    owner = db_session.get(Owner, payload.owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="飼い主が見つかりません",
        )

    dog = Dog(name=payload.name, birthday=payload.birthday, gender=payload.gender)
    db_session.add(dog)
    db_session.flush()

    owner_dog = OwnerDog(
        owner_id=owner.owner_id,
        dog_id=dog.dog_id,
    )
    db_session.add(owner_dog)
    db_session.commit()
    db_session.refresh(dog)

    return DogCreateResponse(
        dog_id=dog.dog_id,
        owner_id=owner.owner_id,
        name=dog.name,
        birthday=dog.birthday,
        gender=dog.gender,
    )


@router.post(
    "/{dog_id}/owners",
    response_model=DogOwnerAddResponse,
    status_code=status.HTTP_201_CREATED,
    summary="犬に飼い主を追加する",
    description="ログインIDで指定した飼い主を犬に紐づけます。",
    response_description="紐づけた犬と飼い主の情報",
    responses={
        404: {"description": "指定した犬またはログインIDに一致する飼い主が存在しません。"},
        409: {"description": "犬と飼い主は既に紐づけられています。"},
    },
)
def add_dog_owner(
    dog_id: DogIdPath,
    payload: DogOwnerAddRequest,
    db_session: Session = Depends(get_dog_db_session),
) -> DogOwnerAddResponse:
    dog = db_session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="犬が見つかりません",
        )

    owner = db_session.execute(
        select(Owner).where(Owner.login_id == payload.login_id),
    ).scalar_one_or_none()
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ログインIDに一致する飼い主が見つかりません",
        )

    if any(owner_dog.owner_id == owner.owner_id for owner_dog in dog.owners):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="既に紐づけられています",
        )

    owner_dog = OwnerDog(owner_id=owner.owner_id, dog_id=dog.dog_id)
    db_session.add(owner_dog)
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="既に紐づけられています",
        ) from None

    return DogOwnerAddResponse(
        dog=DogIdName(dog_id=dog.dog_id, name=dog.name),
        owner=OwnerIdName(owner_id=owner.owner_id, name=owner.name),
    )


@router.patch(
    "/{dog_id}",
    response_model=DogResponse,
    summary="犬のプロフィールを更新する",
    description="指定した犬の名前、誕生日、性別のうち、送信された項目を更新します。",
    response_description="更新した犬の情報",
    responses={404: {"description": "指定した犬が存在しません。"}},
)
def update_dog(
    dog_id: DogIdPath,
    payload: DogUpdateRequest,
    db_session: Session = Depends(get_dog_db_session),
) -> Dog:
    dog = db_session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="犬が見つかりません",
        )

    if payload.name is not None:
        dog.name = payload.name

    if "birthday" in payload.model_fields_set:
        dog.birthday = payload.birthday

    if "gender" in payload.model_fields_set:
        dog.gender = payload.gender

    db_session.commit()
    db_session.refresh(dog)
    return dog


@router.get(
    "/{dog_id}/owners",
    response_model=DogOwnersResponse,
    summary="犬に紐づく飼い主を取得する",
    description="指定した犬のプロフィールと、その犬に紐づく飼い主の一覧を返します。",
    response_description="犬の情報と紐づく飼い主の一覧",
    responses={404: {"description": "指定した犬が存在しません。"}},
)
def list_dog_owners(
    dog_id: DogIdPath,
    db_session: Session = Depends(get_dog_db_session),
) -> DogOwnersResponse:
    dog = db_session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="犬が見つかりません",
        )

    owners = [
        DogOwnerSummary(
            owner_id=owner_dog.owner.owner_id,
            name=owner_dog.owner.name,
            role=owner_dog.role,
        )
        for owner_dog in dog.owners
    ]

    return DogOwnersResponse(
        dog_id=dog.dog_id,
        dog_name=dog.name,
        birthday=dog.birthday,
        gender=dog.gender,
        owners=owners,
    )
