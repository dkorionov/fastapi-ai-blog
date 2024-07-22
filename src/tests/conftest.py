from typing import AsyncGenerator

import httpx
import pytest
from commands.user import create_admin_command
from core.config import MainSettings, create_settings, create_test_settings
from db.models.base import PgBaseModel
from db.utils import clean_db, create_database, drop_database
from dotenv import load_dotenv
from fastapi import FastAPI
from httpx import ASGITransport
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)
from web import server as init_server

load_dotenv()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
def get_test_settings() -> MainSettings:
    return create_test_settings()


@pytest.fixture(scope="session")
def get_db_url_and_name(get_test_settings: MainSettings) -> tuple[str, str]:
    return str(PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username=get_test_settings.db.DB_USER,
        password=get_test_settings.db.DB_PASSWORD,
        host=get_test_settings.db.DB_HOST,
        port=get_test_settings.db.DB_PORT,
    )), get_test_settings.db.DB_NAME


@pytest.fixture(scope="session", autouse=True)
async def setup_database(get_db_url_and_name: tuple[str, str]) -> AsyncGenerator:
    db_url, db_name = get_db_url_and_name
    try:
        print("Creating Database")
        yield await create_database(db_url, db_name)
    finally:
        print("Dropping Database")
        await drop_database(db_url, db_name)


@pytest.fixture(scope="session")
def engine(get_test_settings: MainSettings, setup_database):
    return create_async_engine(get_test_settings.db.DB_CONNECTION_URL, echo=True, future=True)


@pytest.fixture(scope="session", autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        print("Creating tables")
        await conn.run_sync(PgBaseModel.metadata.create_all)


@pytest.fixture(scope="function", autouse=True)
async def clean_database(engine, get_test_settings):
    await clean_db(db_url=get_test_settings.db.DB_CONNECTION_URL)


@pytest.fixture
async def fastapi_app() -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = init_server()
    application.dependency_overrides[create_settings] = create_test_settings
    return application


@pytest.fixture
async def async_client(fastapi_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Fixture for creating test client.

    :param fastapi_app: fastapi application.
    :return: test client.
    """
    async with httpx.AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def create_admin(get_test_settings: MainSettings, create_tables):
    await create_admin_command(
        username=get_test_settings.admin.username,
        email=get_test_settings.admin.email,
        password=get_test_settings.admin.password,
        settings=get_test_settings
    )



## providers
