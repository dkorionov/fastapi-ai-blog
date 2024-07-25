from __future__ import annotations

import dataclasses
import typing
from datetime import datetime

from pydantic import BaseModel, Field

if typing.TYPE_CHECKING:
    from domains.dto import CommentDTO, UserDTO


class PostDTO(BaseModel):
    id: int | None = Field(default=None)
    title: str
    content: str
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    author_id: int
    author: UserDTO | None = Field(default=None)
    post_comments: set[CommentDTO] | None = Field(default=None)


@dataclasses.dataclass(frozen=True)
class PostFilter:
    author_id: int | None
    title: str | None
    created_at: datetime | None
    updated_at: datetime | None

    def to_dict(self):
        return dataclasses.asdict(self)
