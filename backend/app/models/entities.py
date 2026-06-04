from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Owner(Base):
    __tablename__ = "owners"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    login_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    dogs: Mapped[list["OwnerDog"]] = relationship(back_populates="owner")


class Dog(Base):
    __tablename__ = "dogs"
    __table_args__ = (
        CheckConstraint(
            "gender IN ('male', 'female', 'unknown')",
            name="ck_dogs_gender",
        ),
    )

    dog_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(Text, nullable=True)

    owners: Mapped[list["OwnerDog"]] = relationship(back_populates="dog")


class OwnerDog(Base):
    __tablename__ = "owner_dogs"
    __table_args__ = (
        UniqueConstraint("owner_id", "dog_id", name="uq_owner_dogs_owner_id_dog_id"),
    )

    owner_dog_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("owners.owner_id", ondelete="CASCADE"),
        nullable=False,
    )
    dog_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dogs.dog_id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str | None] = mapped_column(String, nullable=True)

    owner: Mapped[Owner] = relationship(back_populates="dogs")
    dog: Mapped[Dog] = relationship(back_populates="owners")
