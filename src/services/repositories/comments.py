from typing import Any, Sequence

from db.models import CommentModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from services.repositories.base import PgRepositoryMixin


class CommentRepository(PgRepositoryMixin):
    model = CommentModel

    async def get_comments_with_author(
            self,
            session: AsyncSession,
            filters: dict[str, Any] | None = None,
            ordering: list[str] | None = None,
            limit: int = 10,
            offset: int = 0
    ) -> Sequence[CommentModel]:
        stmt = select(self.model).options(joinedload(self.model.author))
        stmt = self.filter_query(self.model, stmt, filters, ordering, limit, offset)
        comments = await session.execute(stmt)
        return comments.scalars().all()
