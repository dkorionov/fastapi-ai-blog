from typing import TypeVar

import pydantic

from .comment import CommentDTO
from .post import PostDTO
from .user import UserDTO

__all__ = [
    "PostDTO",
    "UserDTO",
    "CommentDTO",
    "AbstractDTO",
]

AbstractDTO = TypeVar("AbstractDTO", bound=pydantic.BaseModel)
