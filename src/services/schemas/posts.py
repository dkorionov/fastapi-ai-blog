from datetime import datetime

from pydantic import BaseModel

from services.schemas.user import OutputUserSchema


class InputPostSchema(BaseModel):
    title: str
    content: str


class BasePostSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    author_id: int


class PostWithAuthorSchema(BasePostSchema):
    author: OutputUserSchema
