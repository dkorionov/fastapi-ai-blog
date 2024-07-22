from typing import List

from services.schemas.user import BaseUser
from services.security import JwtAuthService

from domains.controllers.base import BaseController
from domains.repositories.user import UserReadDBRepository, UserWriteDBRepository


class UserController(BaseController):
    def __init__(
            self,
            db_read_repo: UserReadDBRepository,
            db_write_repo: UserWriteDBRepository,
            oauth_service: JwtAuthService

    ):
        self.db_read_repo = db_read_repo
        self.db_write_repo = db_write_repo
        self.oauth_service = oauth_service

    async def list(self, filters: dict | None = None) -> list[BaseUser]:
        async with self.db_read_repo.session_factory() as session:
            user_data = await self.db_read_repo.list(session, filters)
            return [BaseUser.model_validate(user, from_attributes=True) for user in user_data]

    async def get(self, item_id: int) -> BaseUser:
        async with self.db_read_repo.session_factory() as session:
            user_data = await self.db_read_repo.get(session, item_id)
            return BaseUser.model_validate(user_data, from_attributes=True)

    async def create(self, user: BaseUser) -> BaseUser:
        async with self.db_write_repo.session_factory() as session:
            user_data = user.model_dump()
            user_data["password"] = self.oauth_service.hash_password(user_data["password"])
            created_user = await self.db_write_repo.create(session, user_data)
            return BaseUser.model_validate(created_user, from_attributes=True)

    async def create_user_bulk(self, users: List[BaseUser]) -> int:
        async with self.db_write_repo.session_factory() as session:
            users_to_create = []
            for user_to_create in users:
                user_data = user_to_create.model_dump()
                user_data["password"] = self.oauth_service.hash_password(user_data["password"])
                users_to_create.append(user_data)
            return await self.db_write_repo.create_bulk(session, users_to_create)

    async def update(self, user: BaseUser) -> BaseUser:
        async with self.db_write_repo.session_factory() as session:
            user_data = user.model_dump()
            updated_user = await self.db_write_repo.update(session, user_data["id"], **user_data)
            return BaseUser.model_validate(updated_user, from_attributes=True)

    async def delete(self, item_id: int):
        async with self.db_write_repo.session_factory() as session:
            await self.db_write_repo.delete(session, item_id)

    async def set_password(self, user_id: int, password: str):
        hashed_password = self.oauth_service.hash_password(password)
        async with self.db_write_repo.session_factory() as session:
            return await self.db_write_repo.set_password(session, user_id, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.oauth_service.hash_password(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.oauth_service.verify_password(plain_password, hashed_password)
