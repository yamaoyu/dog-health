from __future__ import annotations

from pydantic import BaseModel
from psycopg import OperationalError, connect

from app.config import Settings


class DatabaseStatus(BaseModel):
    connected: bool
    host: str
    port: int
    name: str
    user: str


def check_database_connection(settings: Settings) -> DatabaseStatus:
    try:
        with connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            connect_timeout=3,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
    except OperationalError:
        return DatabaseStatus(
            connected=False,
            host=settings.db_host,
            port=settings.db_port,
            name=settings.db_name,
            user=settings.db_user,
        )

    return DatabaseStatus(
        connected=True,
        host=settings.db_host,
        port=settings.db_port,
        name=settings.db_name,
        user=settings.db_user,
    )
