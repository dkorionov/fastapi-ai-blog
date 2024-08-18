import sqlalchemy
from sqlalchemy import create_engine, pool, text

from db.models import PgBaseModel


def clean_db(*, db_url: str) -> None:
    async_engine = create_engine(db_url, poolclass=pool.NullPool, future=True)
    meta = PgBaseModel.metadata
    with async_engine.begin() as conn:
        for table in reversed(meta.sorted_tables):
            conn.execute(
                sqlalchemy.text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;").execution_options(autocommit=True)
            )
        conn.commit()


def create_database(db_url: str, db_name: str) -> None:
    """Create a database."""
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        database_existance = conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        drop_database(db_url, db_name)

    with engine.connect() as conn:
        conn.execute(
            text(
                f'CREATE DATABASE "{db_name}" ENCODING "utf8" TEMPLATE template1',
            ),
        )


def drop_database(db_url: str, db_name: str) -> None:
    """Drop current database."""
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{db_name}' "
            "AND pid <> pg_backend_pid();"
        )
        conn.execute(text(disc_users))
        conn.execute(text(f'DROP DATABASE "{db_name}"'))
