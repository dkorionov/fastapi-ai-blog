from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pydantic
from core.config.constansts import UserRole

if TYPE_CHECKING:
    from domains.dto import CommentDTO, PostDTO


class UserDTO(pydantic.BaseModel):
    __repr_name__ = "User"

    id: int | None = pydantic.Field(default=None)
    username: str
    email: pydantic.EmailStr
    role: UserRole
    password: str
    joined_at: datetime | None = pydantic.Field(default=None)
    updated_at: datetime | None = pydantic.Field(default=None)


class FullUserDTO(UserDTO):
    user_posts: set[PostDTO] | None = pydantic.Field(default=None)
    user_comments: set[CommentDTO] | None = pydantic.Field(default=None)
