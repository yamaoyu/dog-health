from __future__ import annotations

from sqlalchemy import UniqueConstraint

from app.models import Dog, Owner, OwnerDog


def test_owner_model_matches_schema() -> None:
    table = Owner.__table__

    assert table.name == "owners"
    assert table.c.owner_id.primary_key is True
    assert table.c.name.nullable is False


def test_dog_model_matches_schema() -> None:
    table = Dog.__table__

    assert table.name == "dogs"
    assert table.c.dog_id.primary_key is True
    assert table.c.name.nullable is False
    assert table.c.birthday.nullable is False


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
