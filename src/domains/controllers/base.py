from abc import ABC
from typing import Dict, NamedTuple, Type, TypeVar

import pydantic

from domains.repositories.base import (
    PgCreateUpdateDeleteRepository,
    PgGetListRepository,
)

BaseDTO = TypeVar("BaseDTO", bound=pydantic.BaseModel)


class BaseController(ABC):
    pass


class BaseCrudController(BaseController):
    model_dto: Type[BaseDTO]
    read_repo: PgGetListRepository
    write_repo: PgCreateUpdateDeleteRepository

    async def list(
            self, filters: Dict | NamedTuple | None = None,
            offset: int = 0,
            limit: int = 10
    ) -> list[BaseDTO]:
        async with self.read_repo.session_factory() as session:
            users_in_db = await self.read_repo.list(session, filters, offset, limit)
            return [self.model_dto.model_validate(user, from_attributes=True) for user in users_in_db]

    async def get(self, item_id: int) -> BaseDTO:
        async with self.read_repo.session_factory() as session:
            user_in_db = await self.read_repo.get(session, item_id)
            return self.model_dto.model_validate(user_in_db, from_attributes=True)

    async def create(self, item: BaseDTO) -> BaseDTO:
        async with self.write_repo.session_factory() as session:
            created_object = await self.write_repo.create(
                session, item.model_dump(exclude={"id"}, exclude_unset=True)
            )
        return self.model_dto.model_validate(created_object, from_attributes=True)

    async def update(self, item: BaseDTO) -> BaseDTO:
        async with self.write_repo.session_factory() as session:
            updated_user = await self.write_repo.update(
                session,
                item.id,
                item.model_dump(
                    exclude={"id"},
                    exclude_unset=True
                )
            )
            return self.model_dto.model_validate(updated_user, from_attributes=True)

    async def delete(self, item_id: int):
        async with self.write_repo.session_factory() as session:
            await self.write_repo.delete(session, item_id)
