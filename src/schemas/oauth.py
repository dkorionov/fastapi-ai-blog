from pydantic import BaseModel, EmailStr, Field

from schemas.users import OutputUserSchema


class LoginSchema(BaseModel):
    username: str = Field(..., description="User username")
    password: str = Field(..., description="User password")


class RegisterSchema(LoginSchema):
    email: EmailStr = Field(..., description="User email")


class ResponseTokenScheme(OutputUserSchema):
    access_token: str
    refresh_token: str
    access_token_expires_at: float
    refresh_token_expires_at: float


class RefreshTokenInputSchema(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")
