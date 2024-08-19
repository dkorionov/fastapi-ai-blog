import abc
from typing import Any, List, Sequence, Type

from db.models.base import AbstractModel
from sqlalchemy import (
    Row,
    RowMapping,
    Select,
    delete,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.errors import ResourceNotFoundError
from services.errors.base import DuplicateResourceError


class AbstractRepository(abc.ABC):
    pass


class PgRepositoryMixin(AbstractRepository):
    model: Type[AbstractModel]

    async def get(self, session: AsyncSession, obj_id: str | int) -> AbstractModel | Any:
        obj = await session.get(self.model, obj_id)
        if not obj:
            raise ResourceNotFoundError(detail=f"{self.model.__name__} not found with id {obj_id}")
        return obj

    async def list(
            self,
            session: AsyncSession,
            filters: dict[str, Any] | None = None,
            ordering: list[str] | None = None,
            limit: int = 10,
            offset: int = 0
    ) -> Sequence[Row[Any] | RowMapping | Any] | list[Any]:
        stmt = select(self.model)
        stmt = self.filter_query(self.model, stmt, filters, ordering, limit, offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(session: AsyncSession, item: AbstractModel) -> AbstractModel:
        session.add(item)
        try:
            await session.commit()
        except IntegrityError as e:
            raise DuplicateResourceError(detail=str(e.orig))
        await session.refresh(item)
        return item

    async def update(self, session: AsyncSession, obj_id: int, data: dict):
        stmt = update(self.model).where(self.model.id == obj_id).values(data)
        await session.execute(stmt)
        await session.commit()

    async def delete(self, session: AsyncSession, obj_id: int):
        await session.execute(delete(self.model).where(self.model.id == obj_id))
        await session.commit()

    async def create_bulk(self, session: AsyncSession, items: List[AbstractModel]) -> Sequence[Any]:
        session.add_all(items)
        try:
            await session.commit()
        except IntegrityError as e:
            raise DuplicateResourceError(detail=str(e.orig))


    async def update_bulk(self, session: AsyncSession, updates: List[dict]) -> Sequence[Any]:
        results = await session.execute(update(self.model).values(updates).returning(self.model.id))
        return results.scalars().all()

    async def delete_bulk(self, session: AsyncSession, obj_ids: List[int]) -> None:
        await session.execute(delete(self.model).where(self.model.id.in_(obj_ids)))

    @staticmethod
    def filter_query(
            model: Type[AbstractModel],
            stmt: Select,
            filters: dict[str, str] | None = None,
            ordering: List[str] | None = None,
            limit: int = 10,
            offset: int = 0
    ) -> Select:
        if filters:
            for key, value in filters.items():
                if value:
                    stmt = stmt.where(getattr(model, key) == value)

        if ordering:
            for value in ordering:
                if value:
                    if value.startswith("-"):
                        stmt = stmt.order_by(getattr(model, value[1:]).desc())
                    else:
                        stmt = stmt.order_by(getattr(model, value))
        return stmt.offset(offset).limit(limit)
