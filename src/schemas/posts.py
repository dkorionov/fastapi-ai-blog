from datetime import datetime

from pydantic import BaseModel

from schemas.users import OutputUserSchema


class InputPostSchema(BaseModel):
    title: str
    content: str


class UpdatePostSchema(BaseModel):
    title: str | None = None
    content: str | None = None


class BasePostSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    author_id: int


class PostWithAuthorSchema(BasePostSchema):
    author: OutputUserSchema
