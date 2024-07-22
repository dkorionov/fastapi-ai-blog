
from db.models.user import UserTable
from services.errors import ResourceNotFoundError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .base import PgCreateUpdateDeleteRepository, PgGetListRepository


class UserReadDBRepository(PgGetListRepository):
    model = UserTable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_user_creds(self, session: AsyncSession, username: str) -> UserTable:
        query = select(self.model).where(self.model.username == username)
        result: UserTable = (await session.execute(query)).scalars().first()
        if result is None:
            raise ResourceNotFoundError
        return result


class UserWriteDBRepository(PgCreateUpdateDeleteRepository):
    model = UserTable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def set_password(
            self,
            session: AsyncSession,
            user_id: int,
            hashed_password: str
    ):
        await session.execute(
            update(self.model).where(self.model.id == user_id)
            .values(password=hashed_password)
        )
        await session.commit()
        await session.flush()
