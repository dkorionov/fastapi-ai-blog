import abc
from typing import Any, Optional, Sequence, Type, TypeVar

from db.models.base import PgBaseModel
from services.errors import ResourceNotFoundError
from sqlalchemy import Row, RowMapping, delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class BaseRepository(abc.ABC):
    pass


M = TypeVar("M", bound=PgBaseModel)


class PgGetListRepository(BaseRepository):
    model: Type[M]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get(self, session: AsyncSession, obj_id: str | int) -> Optional[M]:
        obj = await session.get(self.model, obj_id)
        if not obj:
            raise ResourceNotFoundError(detail=f"{self.model.__name__} not found with id {obj_id}")
        return obj

    async def list(
            self,
            session: AsyncSession,
            filters: dict[str | Any] | None = None,
    ) -> Sequence[Row[Any] | RowMapping | Any] | list[Any]:
        stmt = select(self.model)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await session.execute(stmt)
        return result.scalars().all()


class PgCreateUpdateDeleteRepository(BaseRepository):
    model: Type[M]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(self, session: AsyncSession, data: dict) -> Optional[M]:
        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(self, session: AsyncSession, obj_id: str | int, **kwargs: Any) -> Optional[M]:
        obj = await session.get(self.model, obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await session.commit()
            await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: str | int):
        await session.execute(delete(self.model).where(self.model.id == obj_id))
        await session.commit()

    async def create_bulk(self, session: AsyncSession, data: list[dict]) -> int:
        try:
            result = await session.scalars(
                insert(self.model).returning(self.model.id),
                data,
            )
            await session.commit()
            return len(list(result.all()))
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    async def update_bulk(self, session: AsyncSession, updates: list[dict]) -> int:
        try:
            result = await session.scalars(
                update(self.model).returning(self.model.id),
                updates
            )
            return len(list(result.all()))

        except SQLAlchemyError as e:
            await session.rollback()
            raise e
