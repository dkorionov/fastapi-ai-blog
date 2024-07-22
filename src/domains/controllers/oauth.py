from services.errors.oauth import InvalidCredentialsError
from services.schemas.oauth import RegisterSchema, ResponseTokenScheme
from services.schemas.user import BaseUser
from services.security import JwtAuthService

from domains.controllers.base import BaseController
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

    async def login(self, username: str, password: str) -> ResponseTokenScheme:
        async with self.read_repo.session_factory() as session:
            user_data = await self.read_repo.get_user_creds(session, username)
            user = BaseUser.model_validate(user_data, from_attributes=True)
        if not self.jwt_service.verify_password(password, user.password):
            raise InvalidCredentialsError
        return ResponseTokenScheme(
            **user.model_dump(),
            **self.jwt_service.generate_jwt_tokens(
                user.id,
            )
        )

    async def register(self, data: RegisterSchema) -> ResponseTokenScheme:
        async with self.write_repo.session_factory() as session:
            data.password = self.jwt_service.hash_password(data.password)
            user_data = await self.write_repo.create(
                session,
                data.model_dump()
            )
            user = BaseUser.model_validate(user_data, from_attributes=True)
            oauth_tokens = self.jwt_service.generate_jwt_tokens(user.id)
        return ResponseTokenScheme(**oauth_tokens, **user.model_dump())

    async def refresh_access_token(self, refresh_token: str) -> ResponseTokenScheme:
        tokens, user_id = self.jwt_service.refresh_token(
            refresh_token,
        )
        async with self.read_repo.session_factory() as session:
            user = await self.read_repo.get(session, user_id)
            user_data = BaseUser.model_validate(user, from_attributes=True)
        return ResponseTokenScheme(
            **user_data.model_dump(),
            **tokens
        )
