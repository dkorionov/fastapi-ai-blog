from db.models import UserModel, UserSettingsModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.errors import ResourceNotFoundError
from services.repositories.base import PgRepositoryMixin


class UserRepository(PgRepositoryMixin):
    model = UserModel

    async def get_by_username(self, session: AsyncSession, username: str) -> UserModel:
        stmt = select(self.model).where(self.model.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise ResourceNotFoundError(detail=f"User not found with username {username}")
        return user

    @staticmethod
    async def create_with_settings(
            session: AsyncSession,
            user: UserModel,
    ) -> UserModel:
        session.add(user)
        await session.flush()
        settings = UserSettingsModel(user_id=user.id)
        session.add(settings)
        await session.commit()
        return user


class UserSettingsRepository(PgRepositoryMixin):
    model = UserSettingsModel



