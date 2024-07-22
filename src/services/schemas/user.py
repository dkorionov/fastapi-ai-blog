from core.config.constansts import UserRole
from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    username: str = Field(..., description="User username")
    email: EmailStr = Field()
    role: UserRole = Field(..., description="User role")


class InputUser(BaseUser):
    password: str = Field(..., description="User password")


class OutputUser(BaseUser):
    id: int = Field(..., description="User id")
