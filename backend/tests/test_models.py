from __future__ import annotations

from sqlalchemy import CheckConstraint, UniqueConstraint

from app.models import Dog, Event, EventType, FoodEvent, Owner, OwnerDog, ToiletEvent, WalkEvent


def test_owner_model_matches_schema() -> None:
    table = Owner.__table__

    assert table.name == "owners"
    assert table.c.owner_id.primary_key is True
    assert table.c.name.nullable is False
    assert table.c.login_id.nullable is False
    assert table.c.login_id.unique is True


def test_dog_model_matches_schema() -> None:
    table = Dog.__table__
    check_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    ]

    assert table.name == "dogs"
    assert table.c.dog_id.primary_key is True
    assert table.c.name.nullable is False
    assert table.c.birthday.nullable is True
    assert table.c.gender.nullable is True
    assert len(check_constraints) == 1
    assert check_constraints[0].name == "ck_dogs_gender"


def test_owner_dog_model_matches_schema() -> None:
    table = OwnerDog.__table__
    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    foreign_key_targets = {
        foreign_key.target_fullname
        for column in (table.c.owner_id, table.c.dog_id)
        for foreign_key in column.foreign_keys
    }

    assert table.name == "owner_dogs"
    assert table.c.owner_dog_id.primary_key is True
    assert table.c.owner_id.nullable is False
    assert table.c.dog_id.nullable is False
    assert table.c.role.nullable is True
    assert foreign_key_targets == {"owners.owner_id", "dogs.dog_id"}
    assert len(unique_constraints) == 1
    assert unique_constraints[0].name == "uq_owner_dogs_owner_id_dog_id"
    assert {column.name for column in unique_constraints[0].columns} == {
        "owner_id",
        "dog_id",
    }


def test_event_type_model_matches_schema() -> None:
    table = EventType.__table__

    assert table.name == "event_types"
    assert table.c.event_type_id.primary_key is True
    assert table.c.code.nullable is False
    assert table.c.code.unique is True
    assert table.c.display_name.nullable is False
    assert table.c.is_active.nullable is False


def test_event_model_matches_schema() -> None:
    table = Event.__table__
    foreign_key_targets = {
        foreign_key.target_fullname
        for column in (table.c.dog_id, table.c.event_type_id)
        for foreign_key in column.foreign_keys
    }

    assert table.name == "events"
    assert table.c.event_id.primary_key is True
    assert table.c.dog_id.nullable is False
    assert table.c.event_type_id.nullable is False
    assert table.c.occurred_at.nullable is False
    assert table.c.memo.nullable is True
    assert foreign_key_targets == {"dogs.dog_id", "event_types.event_type_id"}


def test_walk_event_model_matches_schema() -> None:
    table = WalkEvent.__table__
    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in table.c.event_id.foreign_keys
    }

    assert table.name == "walk_events"
    assert table.c.event_id.primary_key is True
    assert table.c.distance.nullable is True
    assert table.c.time.nullable is True
    assert foreign_key_targets == {"events.event_id"}


def test_food_event_model_matches_schema() -> None:
    table = FoodEvent.__table__
    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in table.c.event_id.foreign_keys
    }

    assert table.name == "food_events"
    assert table.c.event_id.primary_key is True
    assert table.c.menu.nullable is True
    assert table.c.amount.nullable is True
    assert foreign_key_targets == {"events.event_id"}


def test_toilet_event_model_matches_schema() -> None:
    table = ToiletEvent.__table__
    foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in table.c.event_id.foreign_keys
    }

    assert table.name == "toilet_events"
    assert table.c.event_id.primary_key is True
    assert table.c.type.nullable is True
    assert table.c.condition.nullable is True
    assert foreign_key_targets == {"events.event_id"}
