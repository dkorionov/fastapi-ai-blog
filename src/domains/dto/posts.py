from pydantic import BaseModel


class Post(BaseModel):
    id: int | None
    title: str
    content: str
    created_at: float
    updated_at: float
    author_id: int
