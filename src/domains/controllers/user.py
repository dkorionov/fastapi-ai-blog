from typing import List, Sequence

from services.security import JwtAuthService

from domains.controllers.base import BaseCrudController
from domains.dto import UserDTO
from domains.repositories.user import UserReadDBRepository, UserWriteDBRepository


class UserController(BaseCrudController):
    model_dto = UserDTO

    def __init__(
            self,
            read_repo: UserReadDBRepository,
            write_repo: UserWriteDBRepository,
            oauth_service: JwtAuthService

    ):
        self.read_repo: UserReadDBRepository = read_repo
        self.write_repo: UserWriteDBRepository = write_repo
        self.oauth_service: JwtAuthService = oauth_service

    async def create(self, user: UserDTO) -> UserDTO:
        async with self.write_repo.session_factory() as session:
            user_data = user.model_dump(exclude={"id"}, exclude_unset=True)
            user_data["password"] = self.oauth_service.hash_password(user_data["password"])
            created_user = await self.write_repo.create(
                session, user_data
            )
            return UserDTO.model_validate(created_user, from_attributes=True)

    async def create_user_bulk(self, users: List[UserDTO]) -> Sequence[int]:
        async with self.write_repo.session_factory() as session:
            users_to_create = []
            for user in users:
                user_data = user.model_dump(exclude={"id"}, exclude_unset=True)
                user_data["password"] = self.oauth_service.hash_password(user_data["password"])
                users_to_create.append(user_data)
            return await self.write_repo.create_bulk(session, users_to_create)

    async def update(self, user: UserDTO) -> UserDTO:
        async with self.write_repo.session_factory() as session:
            user_data = user.model_dump(exclude={"password"}, exclude_unset=True)
            updated_user = await self.write_repo.update(session, user.id, user_data)
            return UserDTO.model_validate(updated_user, from_attributes=True)

    async def set_password(self, user_id: int, password: str):
        hashed_password = self.oauth_service.hash_password(password)
        async with self.write_repo.session_factory() as session:
            return await self.write_repo.set_password(session, user_id, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.oauth_service.hash_password(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.oauth_service.verify_password(plain_password, hashed_password)
