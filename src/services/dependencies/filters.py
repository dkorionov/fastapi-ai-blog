import datetime
from collections import namedtuple

from domains.dto.post import PostFilter
from fastapi import Query

Pagination = namedtuple("Pagination", ["limit", "offset"])


def get_pagination(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0)
) -> Pagination:
    return Pagination(limit, offset)


def get_post_filters(
        title: str = Query(None),
        author_id: int = Query(None),
        created_at: datetime.datetime = Query(None),
        updated_at: datetime.datetime = Query(None)
) -> PostFilter:
    return PostFilter(
        title=title,
        author_id=author_id,
        created_at=created_at,
        updated_at=updated_at
    )
