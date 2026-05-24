from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.models import Dog, Owner, OwnerDog
from app.routers.dogs import get_dog_db_session


class FakeSession:
    def __init__(self) -> None:
        self.owners: dict[UUID, Owner] = {}
        self.dog_by_id: dict[UUID, Dog] = {}
        self.dogs: list[Dog] = []
        self.owner_dogs: list[OwnerDog] = []
        self.flushed = False
        self.committed = False
        self.refreshed = False

    def add(self, item: Dog | Owner | OwnerDog) -> None:
        if isinstance(item, Dog):
            item.dog_id = uuid4()
            self.dogs.append(item)
            self.dog_by_id[item.dog_id] = item
            return

        if isinstance(item, OwnerDog):
            item.owner_dog_id = uuid4()
            self.owner_dogs.append(item)
            return

        self.owners[item.owner_id] = item

    def get(self, model: type[Owner] | type[Dog], item_id: UUID) -> Owner | Dog | None:
        if model is Owner:
            return self.owners.get(item_id)

        if model is Dog:
            return self.dog_by_id.get(item_id)

        return None

    def flush(self) -> None:
        self.flushed = True

    def commit(self) -> None:
        self.committed = True

    def refresh(self, item: Dog) -> None:
        self.refreshed = True


client = TestClient(app)


def test_create_dog_creates_dog_and_owner_link() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    fake_session.owners[owner_id] = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    app.dependency_overrides[get_dog_db_session] = lambda: fake_session

    response = client.post(
        "/dogs",
        json={
            "owner_id": str(owner_id),
            "name": "  Pochi  ",
            "birthday": "2020-01-01",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert fake_session.flushed is True
    assert fake_session.committed is True
    assert fake_session.refreshed is True
    assert len(fake_session.dogs) == 1
    assert len(fake_session.owner_dogs) == 1
    assert fake_session.dogs[0].name == "Pochi"
    assert fake_session.dogs[0].birthday == date(2020, 1, 1)
    assert fake_session.owner_dogs[0].owner_id == owner_id
    assert fake_session.owner_dogs[0].dog_id == fake_session.dogs[0].dog_id
    assert fake_session.owner_dogs[0].role is None
    assert response.json() == {
        "dog_id": str(fake_session.dogs[0].dog_id),
        "owner_id": str(owner_id),
        "name": "Pochi",
        "birthday": "2020-01-01",
    }


def test_create_dog_rejects_blank_name() -> None:
    response = client.post(
        "/dogs",
        json={
            "owner_id": "00000000-0000-0000-0000-000000000001",
            "name": "   ",
            "birthday": "2020-01-01",
        },
    )

    assert response.status_code == 422


def test_create_dog_returns_not_found_when_owner_missing() -> None:
    fake_session = FakeSession()
    app.dependency_overrides[get_dog_db_session] = lambda: fake_session

    response = client.post(
        "/dogs",
        json={
            "owner_id": "00000000-0000-0000-0000-000000000099",
            "name": "Pochi",
            "birthday": "2020-01-01",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "owner not found"}
    assert fake_session.committed is False
    assert fake_session.dogs == []
    assert fake_session.owner_dogs == []


def test_list_dog_owners_returns_related_owners() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    dog_id = UUID("00000000-0000-0000-0000-000000000010")
    owner = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    dog = Dog(dog_id=dog_id, name="Pochi", birthday=date(2020, 1, 1))
    dog.owners = [OwnerDog(owner_dog_id=uuid4(), owner=owner, dog=dog, role="primary")]
    fake_session.dog_by_id[dog_id] = dog
    app.dependency_overrides[get_dog_db_session] = lambda: fake_session

    response = client.get(f"/dogs/{dog_id}/owners")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "dog_id": str(dog_id),
        "dog_name": "Pochi",
        "birthday": "2020-01-01",
        "owners": [
            {
                "owner_id": str(owner_id),
                "name": "Hanako",
                "role": "primary",
            }
        ],
    }


def test_list_dog_owners_returns_not_found_when_dog_missing() -> None:
    fake_session = FakeSession()
    app.dependency_overrides[get_dog_db_session] = lambda: fake_session

    response = client.get("/dogs/00000000-0000-0000-0000-000000000099/owners")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "dog not found"}
