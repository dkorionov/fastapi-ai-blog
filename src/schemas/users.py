import datetime

from pydantic import BaseModel, EmailStr, Field


class BaseUserSchema(BaseModel):
    username: str = Field(..., description="User username")
    email: EmailStr = Field()


class InputUserSchema(BaseUserSchema):
    password: str = Field(..., description="User password")


class OutputUserSchema(BaseUserSchema):
    id: int = Field(..., description="User id")


class UserSettingsSchema(BaseModel):
    auto_comment_answer: bool = Field(..., description="Auto comment answer")
    auto_answer_delay: datetime.time = Field(..., description="Auto answer delay", examples=["00:05:00"])


class UserWithSettingsSchema(OutputUserSchema):
    settings: UserSettingsSchema


class UpdateUserSettingsSchema(BaseModel):
    auto_comment_answer: bool | None = Field(description="Auto comment answer", default=None)
    auto_answer_delay: datetime.time | None = Field(description="Auto answer delay", examples=["00:05:00"])
