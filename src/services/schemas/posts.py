from pydantic import BaseModel

from services.schemas.user import BaseUser


class InputPost(BaseModel):
    title: str
    content: str


class BasePost(BaseModel):
    id: int
    title: str
    content: str
    created_at: float
    updated_at: float
    author_id: int


class PostWithAuthor(BasePost):
    author = BaseUser
