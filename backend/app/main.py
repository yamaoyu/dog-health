from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import check_database_connection
from app.routers import dogs_router, events_router, login_router, owners_router
from app.schemas.health_check import HealthCheckResponse


settings = get_settings()

tags_metadata = [
    {"name": "health", "description": "APIとdatabaseの稼働状態を確認します。"},
    {"name": "login", "description": "ログインIDを使って飼い主を識別します。"},
    {"name": "owners", "description": "飼い主情報と飼い主に紐づく犬を管理します。"},
    {"name": "dogs", "description": "犬のプロフィールと飼い主との紐づきを管理します。"},
    {"name": "events", "description": "犬の健康関連イベントを登録・取得します。"},
]

app = FastAPI(
    title=settings.app_name,
    description="犬、飼い主、健康関連イベントを管理するAPIです。",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dogs_router)
app.include_router(events_router)
app.include_router(login_router)
app.include_router(owners_router)


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="APIの稼働状態を取得する",
    description="APIとdatabaseの接続状態、実行環境を返します。",
    response_description="APIとdatabaseの現在の稼働状態",
)
def read_health() -> HealthCheckResponse:
    database_status = check_database_connection(settings)

    return HealthCheckResponse(
        status="ok" if database_status.connected else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        database=database_status,
    )
