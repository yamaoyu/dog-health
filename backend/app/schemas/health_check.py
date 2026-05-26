from __future__ import annotations

from pydantic import BaseModel

from app.db.database import DatabaseStatus


class HealthCheckResponse(BaseModel):
    status: str
    app: str
    environment: str
    database: DatabaseStatus
