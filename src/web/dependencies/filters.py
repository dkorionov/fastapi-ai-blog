from fastapi import Query
from services.filters import Pagination, PostFilter


def get_pagination(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0)
) -> Pagination:
    return Pagination(limit, offset)


def get_ordering(
        order_by: list[str] = Query(None)
) -> list[str]:
    return order_by


def get_post_filters(
        title: str = Query(None),
        author_id: int = Query(None),

) -> PostFilter:
    return PostFilter(
        title=title,
        author_id=author_id,
    )
