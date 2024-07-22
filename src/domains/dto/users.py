import pydantic
from core.config.constansts import UserRole


class UserDTO(pydantic.BaseModel):
    id: int | None
    username: str
    email: pydantic.EmailStr
    role: UserRole
    password: str
