from functools import lru_cache
from typing import List

from pydantic import Field, PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class EnvironmentSettings(BaseEnvSettings):
    is_production: bool = Field(default=False, alias="PRODUCTION")
    is_development: bool = Field(default=False, alias="DEVELOPMENT")
    is_testing: bool = Field(default=False, alias="TESTING")
    is_local: bool = Field(default=False, alias="LOCAL")


class PostgresDBSettings(BaseEnvSettings):
    DB_USER: str = Field(validation_alias="DB_USER")
    DB_PASSWORD: str = Field(validation_alias="DB_PASSWORD")
    DB_HOST: str = Field(validation_alias="DB_HOST")
    DB_PORT: int = Field(validation_alias="DB_PORT")
    DB_NAME: str = Field(validation_alias="DB_NAME")
    DB_CONNECTION_URL: str | None = Field(default=None)
    MIGRATIONS_PATH: str = Field(default="src/db/migrations")
    ALEMBIC_CONFIG_PATH: str = Field(default="src/db/alembic.ini")
    ECHO_SQL: bool = Field(default=False)
    POOL_SIZE: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    MAX_OVERFLOW: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    POOL_TIMEOUT: int = Field(default=30, validation_alias="DB_POOL_TIMEOUT")
    POOL_RECYCLE: int = Field(default=900, validation_alias="DB_POOL_RECYCLE")

    @field_validator("DB_CONNECTION_URL", mode="after")
    @classmethod
    def get_db_connection_url(cls, value: str | None, info: ValidationInfo) -> PostgresDsn | str:
        if value is not None:
            return value

        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=info.data.get("DB_USER"),
                password=info.data.get("DB_PASSWORD"),
                host=info.data.get("DB_HOST"),
                port=info.data.get("DB_PORT"),
                path=info.data.get("DB_NAME"),
            )
        )


class CORSSettings(BaseEnvSettings):
    ALLOW_ORIGIN: List[str] = Field(validation_alias="CORS_ALLOW_ORIGINS", default=["*"])
    ALLOW_METHODS: List[str] = Field(validation_alias="CORS_ALLOW_METHODS", default=["*"])
    ALLOW_HEADERS: List[str] = Field(validation_alias="CORS_ALLOW_HEADERS", default=["*"])
    ALLOW_CREDENTIALS: bool = Field(validation_alias="CORS_ALLOW_CREDENTIALS", default=False)


class AdminSettings(BaseEnvSettings):
    username: str = Field(validation_alias="ADMIN_USERNAME")
    password: str = Field(validation_alias="ADMIN_PASSWORD")
    email: str = Field(validation_alias="ADMIN_EMAIL")


class SecuritySettings(BaseEnvSettings):
    SECRET_KEY: str = Field(validation_alias="SECRET_KEY")
    ALGORITHM: str = Field(validation_alias="ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(validation_alias="ACCESS_TOKEN_EXPIRES_MINUTES", default=60 * 24 * 7)
    REFRESH_TOKEN_EXPIRES_MINUTES: int = Field(validation_alias="REFRESH_TOKEN_EXPIRES_MINUTES", default=60 * 24 * 7)


class MainSettings(BaseEnvSettings):
    db: PostgresDBSettings
    admin: AdminSettings
    cors: CORSSettings
    env: EnvironmentSettings
    security: SecuritySettings


@lru_cache(maxsize=1)
def create_settings() -> MainSettings:
    return MainSettings(
        db=PostgresDBSettings(),
        admin=AdminSettings(),
        cors=CORSSettings(),
        env=EnvironmentSettings(),
        security=SecuritySettings(),
    )


@lru_cache(maxsize=1)
def create_test_settings() -> MainSettings:
    postgres_db = PostgresDBSettings(
        DB_NAME="test_db",
    )
    return MainSettings(
        db=postgres_db,
        admin=AdminSettings(
            username="admin",
            email="admin@mail.com",
            password="admin",
        ),
        cors=CORSSettings(
            ALLOW_ORIGIN=["*"],
            ALLOW_METHODS=["GET", "POST", "PUT", "DELETE"],
            ALLOW_HEADERS=["*"],
            ALLOW_CREDENTIALS=True,
        ),
        env=EnvironmentSettings(),
        security=SecuritySettings(
            SECRET_KEY="test_secret"
        ),
    )
