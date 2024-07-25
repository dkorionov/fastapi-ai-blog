from pydantic import BaseModel, EmailStr, Field


class BaseUserSchema(BaseModel):
    username: str = Field(..., description="User username")
    email: EmailStr = Field()


class InputUserSchema(BaseUserSchema):
    password: str = Field(..., description="User password")


class OutputUserSchema(BaseUserSchema):
    id: int = Field(..., description="User id")
