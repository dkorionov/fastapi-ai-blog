from typing import List

from services.security import JwtAuthService

from domains.controllers.base import BaseController
from domains.dto.users import UserDTO
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

    async def list(self, filters: dict | None = None) -> list[UserDTO]:
        async with self.db_read_repo.session_factory() as session:
            users_in_db = await  self.db_read_repo.list(session, filters)
            return [UserDTO.model_validate(user, from_attributes=True) for user in users_in_db]

    async def get(self, item_id: int) -> UserDTO:
        async with self.db_read_repo.session_factory() as session:
            user_in_db = await self.db_read_repo.get(session, item_id)
            return UserDTO.model_validate(user_in_db, from_attributes=True)

    async def create(self, user: UserDTO) -> UserDTO:
        async with self.db_write_repo.session_factory() as session:
            user_data = user.model_dump(exclude={"id"})
            user_data["password"] = self.oauth_service.hash_password(user_data["password"])
            created_user = await self.db_write_repo.create(
                session, user_data
            )
            return UserDTO.model_validate(created_user, from_attributes=True)

    async def create_user_bulk(self, users: List[UserDTO]) -> int:
        async with self.db_write_repo.session_factory() as session:
            users_to_create = []
            for user in users:
                user_data = user.model_dump(exclude={"id"})
                user_data["password"] = self.oauth_service.hash_password(user_data["password"])
                users_to_create.append(user_data)
            return await self.db_write_repo.create_bulk(session, users_to_create)

    async def update(self, user: UserDTO) -> UserDTO:
        async with self.db_write_repo.session_factory() as session:
            updated_user = await self.db_write_repo.update(session, user.id, **user.model_dump())
            return UserDTO.model_validate(updated_user, from_attributes=True)

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
