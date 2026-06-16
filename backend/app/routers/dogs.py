from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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


def get_dog_db_session() -> Generator[Session, None, None]:
    yield from get_db_session()


@router.post("", response_model=DogCreateResponse, status_code=status.HTTP_201_CREATED)
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
)
def add_dog_owner(
    dog_id: UUID,
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


@router.patch("/{dog_id}", response_model=DogResponse)
def update_dog(
    dog_id: UUID,
    payload: DogUpdateRequest,
    db_session: Session = Depends(get_dog_db_session),
) -> Dog:
    dog = db_session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="犬が見つかりません",
        )

    if "name" in payload.model_fields_set:
        dog.name = payload.name

    if "birthday" in payload.model_fields_set:
        dog.birthday = payload.birthday

    if "gender" in payload.model_fields_set:
        dog.gender = payload.gender

    db_session.commit()
    db_session.refresh(dog)
    return dog


@router.get("/{dog_id}/owners", response_model=DogOwnersResponse)
def list_dog_owners(
    dog_id: UUID,
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
