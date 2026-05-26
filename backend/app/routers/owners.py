from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.entities import Owner
from app.schemas.owners import OwnerCreateRequest, OwnerDogSummary, OwnerDogsResponse, OwnerResponse


router = APIRouter(prefix="/owners", tags=["owners"])


def get_owner_db_session() -> Generator[Session, None, None]:
    yield from get_db_session()


@router.post("", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("/{owner_id}/dogs", response_model=OwnerDogsResponse)
def list_owner_dogs(
    owner_id: UUID,
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
        )
        for owner_dog in owner.dogs
    ]

    return OwnerDogsResponse(
        owner_id=owner.owner_id,
        owner_name=owner.name,
        dogs=dogs,
    )
