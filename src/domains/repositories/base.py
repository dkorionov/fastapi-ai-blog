import abc
from functools import wraps
from typing import Any, Callable, Optional, Sequence, Type, TypeVar

from db.models.base import PgBaseModel
from services.errors import ResourceNotFoundError
from services.errors.base import DuplicateResourceError
from sqlalchemy import (
    CursorResult,
    Result,
    Row,
    RowMapping,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class BaseRepository(abc.ABC):
    pass


M = TypeVar("M", bound=PgBaseModel)

T = TypeVar("T")


def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            raise DuplicateResourceError(detail=", ".join(e.detail))

    return wrapper


class PgGetListRepository(BaseRepository):
    model: Type[M]
    session_factory: async_sessionmaker[AsyncSession]

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
            filters: dict[str | str | Any] | None = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None
    ) -> Sequence[Row[Any] | RowMapping | Any] | list[Any]:
        stmt = select(self.model)
        if filters:
            for key, value in filters.items():
                if value:
                    stmt = stmt.where(getattr(self.model, key) == value)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()


class PgCreateUpdateDeleteRepository(BaseRepository):
    model: Type[M]
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    @handle_errors
    async def create(self, session: AsyncSession, data: M) -> M:
        _ = data.pop("id", None)
        obj = self.model(**data)
        session.add(obj)
        return obj

    @handle_errors
    async def update(self, session: AsyncSession, obj_id: int, data: dict) -> M:
        stmt = update(self.model).where(self.model.id == obj_id).values(data).returning(self.model)
        result = await session.execute(stmt)
        return result.scalars().one()

    async def delete(self, session: AsyncSession, obj_id: int):
        return await session.execute(delete(self.model).where(self.model.id == obj_id))

    @handle_errors
    async def create_bulk(self, session: AsyncSession, data: list[dict]) -> Result[tuple[Any]]:
        stmt = insert(self.model).values(data).returning(self.model.id)
        return await session.execute(stmt)

    @handle_errors
    async def update_bulk(self, session: AsyncSession, updates: list[dict]) -> CursorResult[Any]:
        return await session.execute(update(self.model).values(updates))

    async def delete_bulk(self, session: AsyncSession, obj_ids: list[int]) -> Result[tuple[Any]]:
        return await session.execute(delete(self.model).where(self.model.id.in_(obj_ids)))
