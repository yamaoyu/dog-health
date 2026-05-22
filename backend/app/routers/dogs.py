from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import get_db_session
from app.models.entities import Dog, Owner, OwnerDog
from app.schemas.dogs import DogCreateRequest, DogCreateResponse, DogOwnerSummary, DogOwnersResponse


router = APIRouter(prefix="/dogs", tags=["dogs"])
settings = get_settings()


def get_dog_db_session() -> Generator[Session, None, None]:
    yield from get_db_session(settings)


@router.post("", response_model=DogCreateResponse, status_code=status.HTTP_201_CREATED)
def create_dog(
    payload: DogCreateRequest,
    db_session: Session = Depends(get_dog_db_session),
) -> DogCreateResponse:
    owner = db_session.get(Owner, payload.owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="owner not found",
        )

    dog = Dog(name=payload.name, birthday=payload.birthday)
    db_session.add(dog)
    db_session.flush()

    owner_dog = OwnerDog(
        owner_id=owner.owner_id,
        dog_id=dog.dog_id,
        role=payload.role,
    )
    db_session.add(owner_dog)
    db_session.commit()
    db_session.refresh(dog)

    return DogCreateResponse(
        dog_id=dog.dog_id,
        owner_id=owner.owner_id,
        name=dog.name,
        birthday=dog.birthday,
        role=owner_dog.role,
    )


@router.get("/{dog_id}/owners", response_model=DogOwnersResponse)
def list_dog_owners(
    dog_id: UUID,
    db_session: Session = Depends(get_dog_db_session),
) -> DogOwnersResponse:
    dog = db_session.get(Dog, dog_id)
    if dog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dog not found",
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
        owners=owners,
    )
