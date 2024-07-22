import sqlalchemy
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import create_async_engine

from db.models import PgBaseModel


async def clean_db(*, db_url: str) -> None:
    async_engine = create_async_engine(db_url, poolclass=pool.NullPool, future=True)
    meta = PgBaseModel.metadata
    async with async_engine.begin() as conn:
        for table in reversed(meta.sorted_tables):
            await conn.execute(
                sqlalchemy.text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;").execution_options(autocommit=True)
            )
        await conn.commit()


async def create_database(db_url: str, db_name: str) -> None:
    """Create a database."""
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database(db_url, db_name)

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f'CREATE DATABASE "{db_name}" ENCODING "utf8" TEMPLATE template1',
            ),
        )


async def drop_database(db_url: str, db_name: str) -> None:
    """Drop current database."""
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{db_name}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{db_name}"'))
