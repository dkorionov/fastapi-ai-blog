from typing import Optional

from core.config.constansts import UserRole
from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    id: Optional[int] = Field(description="User id")
    username: str = Field(..., description="User username")
    email: EmailStr = Field()
    role: UserRole = Field(..., description="User role", )
    password: str = Field(..., description="User hashed password")
