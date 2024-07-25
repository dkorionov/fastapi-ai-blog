from services.errors.oauth import InvalidCredentialsError
from services.security import JwtAuthService

from domains.controllers.base import BaseController
from domains.dto import UserDTO
from domains.repositories.user import UserReadDBRepository, UserWriteDBRepository


class OauthController(BaseController):
    def __init__(
            self,
            read_repo: UserReadDBRepository,
            write_repo: UserWriteDBRepository,
            jwt_service: JwtAuthService,
    ):
        self.read_repo = read_repo
        self.write_repo = write_repo
        self.jwt_service = jwt_service

    async def login(self, username: str, password: str) -> tuple[UserDTO, dict[str, str]]:
        async with self.read_repo.session_factory() as session:
            user_data = await self.read_repo.get_user_creds(session, username)
        user = UserDTO.model_validate(user_data, from_attributes=True)
        if not self.jwt_service.verify_password(password, user.password):
            raise InvalidCredentialsError
        return user, self.jwt_service.generate_jwt_tokens(user.id)

    async def register(self, user_data: dict) -> tuple[UserDTO, dict[str, str]]:
        user_data["password"] = self.jwt_service.hash_password(user_data["password"])
        async with self.write_repo.session_factory() as session:
            created_user = await self.write_repo.create(
                session,
                user_data
            )
        user = UserDTO.model_validate(created_user, from_attributes=True)
        tokens = self.jwt_service.generate_jwt_tokens(user.id)
        return user, tokens

    async def refresh_access_token(self, refresh_token: str) -> tuple[UserDTO, dict[str, str]]:
        tokens, user_id = self.jwt_service.refresh_token(
            refresh_token,
        )
        async with self.read_repo.session_factory() as session:
            user = await self.read_repo.get(session, user_id)
            user_data = UserDTO.model_validate(user, from_attributes=True)
        return user_data, tokens
