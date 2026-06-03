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
        if any(owner.login_id in self.duplicate_login_ids for owner in self.owners.values()):
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


def test_create_owner_rejects_non_string_name() -> None:
    response = client.post("/owners", json={"name": None, "login_id": "hanako"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, 名前は文字列で入力してください"


def test_create_owner_rejects_blank_login_id() -> None:
    response = client.post("/owners", json={"name": "Hanako", "login_id": "   "})

    assert response.status_code == 422


def test_create_owner_rejects_non_string_login_id() -> None:
    response = client.post("/owners", json={"name": "Hanako", "login_id": None})

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, ログインIDは文字列で入力してください"


def test_create_owner_returns_conflict_when_login_id_exists() -> None:
    fake_session = FakeSession()
    fake_session.duplicate_login_ids.add("hanako")
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.post("/owners", json={"name": "Hanako", "login_id": "hanako"})

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "このログインIDは既に使用されています"}
    assert fake_session.rolled_back is True


def test_update_owner_updates_name_only() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    owner = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    fake_session.owners[owner_id] = owner
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.patch(f"/owners/{owner_id}", json={"name": "  Taro  "})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_session.committed is True
    assert fake_session.refreshed is True
    assert owner.name == "Taro"
    assert owner.login_id == "hanako"
    assert response.json() == {
        "owner_id": str(owner_id),
        "name": "Taro",
        "login_id": "hanako",
    }


def test_update_owner_updates_login_id_only() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    owner = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    fake_session.owners[owner_id] = owner
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.patch(f"/owners/{owner_id}", json={"login_id": "  taro  "})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert owner.name == "Hanako"
    assert owner.login_id == "taro"
    assert response.json() == {
        "owner_id": str(owner_id),
        "name": "Hanako",
        "login_id": "taro",
    }


def test_update_owner_updates_name_and_login_id() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    owner = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    fake_session.owners[owner_id] = owner
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.patch(
        f"/owners/{owner_id}",
        json={"name": "Taro", "login_id": "taro"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert owner.name == "Taro"
    assert owner.login_id == "taro"
    assert response.json() == {
        "owner_id": str(owner_id),
        "name": "Taro",
        "login_id": "taro",
    }


def test_update_owner_returns_not_found_when_owner_missing() -> None:
    fake_session = FakeSession()
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.patch(
        "/owners/00000000-0000-0000-0000-000000000099",
        json={"name": "Taro"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "飼い主が見つかりません"}
    assert fake_session.committed is False


def test_update_owner_returns_conflict_when_login_id_exists() -> None:
    fake_session = FakeSession()
    owner_id = UUID("00000000-0000-0000-0000-000000000001")
    fake_session.owners[owner_id] = Owner(owner_id=owner_id, name="Hanako", login_id="hanako")
    fake_session.duplicate_login_ids.add("taro")
    app.dependency_overrides[get_owner_db_session] = lambda: fake_session

    response = client.patch(f"/owners/{owner_id}", json={"login_id": "taro"})

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "このログインIDは既に使用されています"}
    assert fake_session.rolled_back is True


def test_update_owner_rejects_blank_name() -> None:
    response = client.patch(
        "/owners/00000000-0000-0000-0000-000000000001",
        json={"name": "   "},
    )

    assert response.status_code == 422


def test_update_owner_rejects_non_string_login_id() -> None:
    response = client.patch(
        "/owners/00000000-0000-0000-0000-000000000001",
        json={"login_id": None},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, ログインIDは文字列で入力してください"


def test_update_owner_rejects_empty_request_body() -> None:
    response = client.patch(
        "/owners/00000000-0000-0000-0000-000000000001",
        json={},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, 更新する項目を指定してください"


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
    assert response.json() == {"detail": "飼い主が見つかりません"}
