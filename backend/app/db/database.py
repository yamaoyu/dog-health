from __future__ import annotations

from collections.abc import Generator

from pydantic import BaseModel
from psycopg import OperationalError, connect
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Settings, get_settings


class DatabaseStatus(BaseModel):
    connected: bool
    host: str
    port: int
    name: str
    user: str


class Base(DeclarativeBase):
    pass


def create_engine_from_settings(settings: Settings) -> Engine:
    return create_engine(
        settings.sqlalchemy_database_url,
        pool_pre_ping=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


settings = get_settings()
engine = create_engine_from_settings(settings)
session_factory = create_session_factory(engine)


def get_db_session() -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


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
