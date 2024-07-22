from contextlib import asynccontextmanager

from core.config import PostgresDBSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:
    def __init__(self, db_settings: PostgresDBSettings):
        self.engine = create_async_engine(
            db_settings.DB_CONNECTION_URL,
            echo=db_settings.ECHO_SQL,
            pool_size=db_settings.POOL_SIZE,
            max_overflow=db_settings.MAX_OVERFLOW,
            pool_timeout=db_settings.POOL_TIMEOUT,
            pool_recycle=db_settings.POOL_RECYCLE,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        session: AsyncSession = self.session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
