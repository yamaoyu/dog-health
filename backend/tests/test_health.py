from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import DatabaseStatus
from app.main import app


client = TestClient(app)


def test_health_returns_expected_shape() -> None:
    with patch("app.main.check_database_connection") as mock_check_database_connection:
        mock_check_database_connection.return_value = DatabaseStatus(
            connected=True,
            host="db",
            port=5432,
            name="dog_health",
            user="dog_health",
        )
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "dog-health-api",
        "environment": "development",
        "database": {
            "connected": True,
            "host": "db",
            "port": 5432,
            "name": "dog_health",
            "user": "dog_health",
        },
    }
