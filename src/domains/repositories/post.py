from db.models import PostModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from domains.dto.post import PostFilter

from .base import PgCreateUpdateDeleteRepository, PgGetListRepository


class PostReadRepository(PgGetListRepository):
    model = PostModel

    async def list_posts_with_author(
            self, session: AsyncSession,
            filters: PostFilter | None = None,
            offset: int = 0,
            limit: int = 10
    ):
        stmt = select(self.model).options(joinedload(self.model.author))
        result = await session.scalars(stmt)
        return result.all()


class PostWriteRepository(PgCreateUpdateDeleteRepository):
    model = PostModel
