from datetime import datetime

from pydantic import BaseModel

from schemas.users import OutputUserSchema


class InputCommentSchema(BaseModel):
    content: str


class OutputCommentSchema(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    author: OutputUserSchema
    created_at: datetime
