from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.models import Owner
from app.routers.login import get_login_db_session


class FakeLoginResult:
    def __init__(self, owner: Owner | None) -> None:
        self.owner = owner

    def scalar_one_or_none(self) -> Owner | None:
        return self.owner


class FakeSession:
    def __init__(self) -> None:
        self.owners_by_login_id: dict[str, Owner] = {}

    def execute(self, statement):  # type: ignore[no-untyped-def]
        where_clause = statement.whereclause
        login_id = where_clause.right.value
        return FakeLoginResult(self.owners_by_login_id.get(login_id))


client = TestClient(app)


def test_login_returns_owner() -> None:
    fake_session = FakeSession()
    owner = Owner(
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
        name="Hanako",
        login_id="hanako",
    )
    fake_session.owners_by_login_id[owner.login_id] = owner
    app.dependency_overrides[get_login_db_session] = lambda: fake_session

    response = client.post("/login", json={"login_id": "  hanako  "})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "owner_id": str(owner.owner_id),
        "name": "Hanako",
        "login_id": "hanako",
    }


def test_login_rejects_blank_login_id() -> None:
    response = client.post("/login", json={"login_id": "   "})

    assert response.status_code == 422


def test_login_returns_not_found_for_unknown_login_id() -> None:
    fake_session = FakeSession()
    app.dependency_overrides[get_login_db_session] = lambda: fake_session

    response = client.post("/login", json={"login_id": "unknown"})

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "owner not found"}
