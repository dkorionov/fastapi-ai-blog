from abc import ABC
from typing import Dict, List, NamedTuple, Sequence, Type

from domains.dto import AbstractDTO
from domains.repositories.base import (
    PgCreateUpdateDeleteRepository,
    PgGetListRepository,
)


class BaseController(ABC):
    model_dto: Type[AbstractDTO]
    red_repo = PgGetListRepository
    write_repo: PgCreateUpdateDeleteRepository


class BaseCrudController(BaseController):
    read_repo: PgGetListRepository
    write_repo: PgCreateUpdateDeleteRepository

    async def list(
            self, filters: Dict | NamedTuple | None = None,
            offset: int = 0,
            limit: int = 10
    ) -> list[AbstractDTO]:
        async with self.read_repo.session_factory() as session:
            users_in_db = await self.read_repo.list(session, filters, offset, limit)
            return [self.model_dto.model_validate(user, from_attributes=True) for user in users_in_db]

    async def get(self, item_id: int) -> AbstractDTO:
        async with self.read_repo.session_factory() as session:
            item = await self.read_repo.get(session, item_id)
            return self.model_dto.model_validate(item, from_attributes=True)

    async def create(self, item: AbstractDTO) -> AbstractDTO:
        async with self.write_repo.session_factory() as session:
            created_object = await self.write_repo.create(
                session, item.model_dump(exclude={"id"}, exclude_unset=True)
            )
            await session.commit()
        return self.model_dto.model_validate(created_object, from_attributes=True)

    async def update(self, item: AbstractDTO) -> AbstractDTO:
        async with self.write_repo.session_factory() as session:
            updated_user = await self.write_repo.update(
                session,
                item.id,
                item.model_dump(
                    exclude={"id"},
                    exclude_unset=True
                )
            )
            await session.commit()
            return self.model_dto.model_validate(updated_user, from_attributes=True)

    async def delete(self, item_id: int):
        async with self.write_repo.session_factory() as session:
            await self.write_repo.delete(session, item_id)
            await session.commit()

    async def create_bulk(self, items: List[AbstractDTO]) -> Sequence[int]:
        async with self.write_repo.session_factory() as session:
            items_to_create = []
            for item in items:
                user_data = item.model_dump(exclude={"id"}, exclude_unset=True)
                items_to_create.append(user_data)
            result = await self.write_repo.create_bulk(session, items_to_create)
            await session.commit()
            return result.scalars().all()

    async def update_bulk(self, items: List[AbstractDTO]) -> Sequence[int]:
        async with self.write_repo.session_factory() as session:
            items_to_update = []
            for item in items:
                item_data = item.model_dump(exclude_unset=True)
                items_to_update.append(item_data)
            result = await self.write_repo.update_bulk(session, items_to_update)
            await session.commit()
            return result.scalars().all()
