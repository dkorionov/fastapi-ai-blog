from __future__ import annotations

import typing
from datetime import datetime

from pydantic import BaseModel, Field

if typing.TYPE_CHECKING:
    from .post import PostDTO
    from .user import UserDTO


class CommentDTO(BaseModel):
    id: int | None = Field(default=None)
    content: str
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    post_id: int
    post: PostDTO | None = Field(default=None)
    author_id: int
    author: UserDTO | None = Field(default=None)
