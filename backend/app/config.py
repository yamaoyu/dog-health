from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    frontend_origins: tuple[str, ...]
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @property
    def sqlalchemy_database_url(self) -> str:
        encoded_password = quote_plus(self.db_password)
        return (
            f"postgresql+psycopg://{self.db_user}:{encoded_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def get_settings() -> Settings:
    frontend_origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5180,http://127.0.0.1:5180",
        ).split(",")
        if origin.strip()
    )

    return Settings(
        app_name=os.getenv("APP_NAME", "dog-health-api"),
        app_env=os.getenv("APP_ENV", "development"),
        frontend_origins=frontend_origins,
        db_host=os.getenv("POSTGRES_HOST", "db"),
        db_port=int(os.getenv("POSTGRES_PORT", "5432")),
        db_name=os.getenv("POSTGRES_DB", "dog_health"),
        db_user=os.getenv("POSTGRES_USER", "dog_health"),
        db_password=os.getenv("POSTGRES_PASSWORD", "dog_health_password"),
    )
