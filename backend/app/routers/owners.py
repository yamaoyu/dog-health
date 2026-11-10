from __future__ import annotations

from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.entities import Owner
from app.schemas.owners import (
    OwnerCreateRequest,
    OwnerDogSummary,
    OwnerDogsResponse,
    OwnerResponse,
    OwnerUpdateRequest,
)


router = APIRouter(prefix="/owners", tags=["owners"])

OwnerIdPath = Annotated[
    UUID,
    Path(
        description="対象となる飼い主のID",
        examples=["00000000-0000-0000-0000-000000000001"],
    ),
]


def get_owner_db_session() -> Generator[Session, None, None]:
    yield from get_db_session()


@router.post(
    "",
    response_model=OwnerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="飼い主を登録する",
    description="名前と重複しないログインIDを指定して飼い主を登録します。",
    response_description="登録した飼い主の情報",
    responses={409: {"description": "指定したログインIDは既に使用されています。"}},
)
def create_owner(
    payload: OwnerCreateRequest,
    db_session: Session = Depends(get_owner_db_session),
) -> Owner:
    owner = Owner(name=payload.name, login_id=payload.login_id)
    db_session.add(owner)
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このログインIDは既に使用されています",
        ) from None
    db_session.refresh(owner)
    return owner


@router.patch(
    "/{owner_id}",
    response_model=OwnerResponse,
    summary="飼い主プロフィールを更新する",
    description="指定した飼い主の名前またはログインIDを更新します。",
    response_description="更新した飼い主の情報",
    responses={
        404: {"description": "指定した飼い主が存在しません。"},
        409: {"description": "指定したログインIDは既に使用されています。"},
    },
)
def update_owner(
    owner_id: OwnerIdPath,
    payload: OwnerUpdateRequest,
    db_session: Session = Depends(get_owner_db_session),
) -> Owner:
    owner = db_session.get(Owner, owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="飼い主が見つかりません",
        )

    if payload.name is not None:
        owner.name = payload.name

    if payload.login_id is not None:
        owner.login_id = payload.login_id

    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このログインIDは既に使用されています",
        ) from None
    db_session.refresh(owner)
    return owner


@router.get(
    "/{owner_id}/dogs",
    response_model=OwnerDogsResponse,
    summary="飼い主に紐づく犬を取得する",
    description="指定した飼い主の情報と、その飼い主に紐づく犬の一覧を返します。",
    response_description="飼い主の情報と紐づく犬の一覧",
    responses={404: {"description": "指定した飼い主が存在しません。"}},
)
def list_owner_dogs(
    owner_id: OwnerIdPath,
    db_session: Session = Depends(get_owner_db_session),
) -> OwnerDogsResponse:
    owner = db_session.get(Owner, owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="飼い主が見つかりません",
        )

    dogs = [
        OwnerDogSummary(
            dog_id=owner_dog.dog.dog_id,
            name=owner_dog.dog.name,
            birthday=owner_dog.dog.birthday,
            gender=owner_dog.dog.gender,
        )
        for owner_dog in owner.dogs
    ]

    return OwnerDogsResponse(
        owner_id=owner.owner_id,
        owner_name=owner.name,
        dogs=dogs,
    )
