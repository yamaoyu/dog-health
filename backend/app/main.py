from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings
from app.database import DatabaseStatus, check_database_connection


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    database: DatabaseStatus


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    database_status = check_database_connection(settings)

    return HealthResponse(
        status="ok" if database_status.connected else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        database=database_status,
    )
