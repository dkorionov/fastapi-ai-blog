from dataclasses import asdict
from typing import Sequence

from db.models import PostModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from services.errors import ResourceNotFoundError
from services.filters import Pagination, PostFilter
from services.repositories.base import PgRepositoryMixin


class PostRepository(PgRepositoryMixin):
    model = PostModel

    async def get_posts_with_author(
            self,
            session: AsyncSession,
            filters: PostFilter,
            ordering: list[str],
            pagination: Pagination
    ) -> Sequence[PostModel]:
        stmt = select(self.model).options(joinedload(self.model.author))
        stmt = self.filter_query(self.model, stmt, asdict(filters), ordering, pagination.limit, pagination.offset)
        posts = await session.execute(stmt)
        return posts.scalars().all()

    async def get_with_author(
            self,
            session: AsyncSession,
            post_id: int
    ) -> PostModel:
        stmt = select(self.model).where(self.model.id == post_id).options(joinedload(self.model.author))
        result = await session.execute(stmt)
        post = result.scalar_one_or_none()
        if not post:
            raise ResourceNotFoundError(detail=f"Post not found with id {post_id}")
        return post
