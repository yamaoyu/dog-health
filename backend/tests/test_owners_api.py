from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.models import Dog, Owner, OwnerDog
from app.routers.owners import get_owner_db_session


class FakeSession:
    def __init__(self) -> None:
        self.owners: dict[UUID, Owner] = {}
        self.items: list[Owner] = []
        self.committed = False
        self.refreshed = False
        self.rolled_back = False
        self.duplicate_login_ids: set[str] = set()

    def add(self, item: Owner) -> None:
        item.owner_id = uuid4()
        self.items.append(item)
        self.owners[item.owner_id] = item

    def get(self, model: type[Owner], item_id: UUID) -> Owner | None:
        if model is not Owner:
            return None

        return self.owners.get(item_id)

    def commit(self) -> None:
        if self.items and self.items[-1].login_id in self.duplicate_login_ids:
            raise IntegrityError("duplicate login_id", params=None, orig=None)

        self.committed = True

    def refresh(self, item: Owner) -> None:
        self.refreshed = True

    def rollback(self) -> None:
        self.rolled_back = True


client = TestClient(app)


def test_create_owner_returns_created_owner() -> None:
    fake_session = FakeSession()
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.post("/owners", json={"name": "  Hanako  ", "login_id": "  hanako  "})

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert fake_session.committed is True
    assert fake_session.refreshed is True
    assert fake_session.items[0].name == "Hanako"
    assert fake_session.items[0].login_id == "hanako"
    assert response.json() == {
        "owner_id": str(fake_session.items[0].owner_id),
        "name": "Hanako",
        "login_id": "hanako",
    }
    assert isinstance(UUID(response.json()["owner_id"]), UUID)


def test_create_owner_rejects_blank_name() -> None:
    response = client.post("/owners", json={"name": "   ", "login_id": "hanako"})

    assert response.status_code == 422


def test_create_owner_rejects_blank_login_id() -> None:
    response = client.post("/owners", json={"name": "Hanako", "login_id": "   "})

    assert response.status_code == 422


def test_create_owner_returns_conflict_when_login_id_exists() -> None:
    fake_session = FakeSession()
    fake_session.duplicate_login_ids.add("hanako")
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.post("/owners", json={"name": "Hanako", "login_id": "hanako"})

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "login_id already exists"}
    assert fake_session.rolled_back is True


def test_list_owner_dogs_returns_related_dogs() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    dog_id = UUID("00000000-0000-0000-0000-000000000010")
    owner = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    dog = Dog(dog_id=dog_id, name="Pochi", birthday=date(2020, 1, 1))
    owner.dogs = [OwnerDog(owner_dog_id=uuid4(), owner=owner, dog=dog, role="primary")]
    fake_session.owners[owner_id] = owner
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.get(f"/owners/{owner_id}/dogs")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "owner_id": str(owner_id),
        "owner_name": "Hanako",
        "dogs": [
            {
                "dog_id": str(dog_id),
                "name": "Pochi",
                "birthday": "2020-01-01",
            }
        ],
    }


def test_list_owner_dogs_returns_not_found_when_owner_missing() -> None:
    fake_session = FakeSession()
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.get("/owners/00000000-0000-0000-0000-000000000099/dogs")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "owner not found"}
