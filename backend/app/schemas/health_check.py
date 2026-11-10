from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.database import DatabaseStatus


class HealthCheckResponse(BaseModel):
    status: str = Field(description="API全体の稼働状態", examples=["ok"])
    app: str = Field(description="アプリケーション名", examples=["dog-health-api"])
    environment: str = Field(description="実行環境", examples=["development"])
    database: DatabaseStatus = Field(description="databaseの接続状態")
