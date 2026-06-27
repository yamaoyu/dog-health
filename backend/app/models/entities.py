from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, String, Text, UniqueConstraint, text
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
    events: Mapped[list["Event"]] = relationship(back_populates="dog")


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


class EventType(Base):
    __tablename__ = "event_types"

    event_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    events: Mapped[list["Event"]] = relationship(back_populates="event_type")


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    dog_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dogs.dog_id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("event_types.event_type_id"),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    dog: Mapped[Dog] = relationship(back_populates="events")
    event_type: Mapped[EventType] = relationship(back_populates="events")
    walk_event: Mapped["WalkEvent | None"] = relationship(back_populates="event")
    food_event: Mapped["FoodEvent | None"] = relationship(back_populates="event")
    toilet_event: Mapped["ToiletEvent | None"] = relationship(back_populates="event")


class WalkEvent(Base):
    __tablename__ = "walk_events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    distance: Mapped[str | None] = mapped_column(Text, nullable=True)
    time: Mapped[str | None] = mapped_column(Text, nullable=True)

    event: Mapped[Event] = relationship(back_populates="walk_event")


class FoodEvent(Base):
    __tablename__ = "food_events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    menu: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[str | None] = mapped_column(Text, nullable=True)

    event: Mapped[Event] = relationship(back_populates="food_event")


class ToiletEvent(Base):
    __tablename__ = "toilet_events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    type: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition: Mapped[str | None] = mapped_column(Text, nullable=True)

    event: Mapped[Event] = relationship(back_populates="toilet_event")
