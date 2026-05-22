from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import check_database_connection
from app.routers import dogs_router, owners_router
from app.schemas.health_check import HealthCheckResponse


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dogs_router)
app.include_router(owners_router)


@app.get("/health", response_model=HealthCheckResponse)
def read_health() -> HealthCheckResponse:
    database_status = check_database_connection(settings)

    return HealthCheckResponse(
        status="ok" if database_status.connected else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        database=database_status,
    )
