from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import get_db_session
from app.models.entities import Owner
from app.schemas.login import LoginRequest, LoginResponse


router = APIRouter(tags=["login"])
settings = get_settings()


def get_login_db_session() -> Generator[Session, None, None]:
    yield from get_db_session(settings)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db_session: Session = Depends(get_login_db_session),
) -> LoginResponse:
    owner = db_session.execute(
        select(Owner).where(Owner.login_id == payload.login_id),
    ).scalar_one_or_none()
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="owner not found",
        )

    return LoginResponse(
        owner_id=owner.owner_id,
        name=owner.name,
        login_id=owner.login_id,
    )
