import dataclasses
import enum
from abc import ABC, abstractmethod
from typing import Tuple, TypeVar

from core.config.constansts import UserRole
from db.models import PgBaseModel

AbstractModel = TypeVar("AbstractModel", bound=PgBaseModel)


class PermissionRoles(enum.Enum):
    admin: str = UserRole.ADMIN.value
    user: str = UserRole.USER.value
    all: str = "all"


@dataclasses.dataclass(frozen=True, slots=False)
class OperationPermission:
    @dataclasses.dataclass(frozen=True, slots=False)
    class Post:
        can_create: str = "posts:create"
        can_update: str = "posts:update"
        can_delete: str = "posts:delete"
        can_view: str = "posts:view"
        can_view_list: str = "posts:view_list"

    @dataclasses.dataclass(frozen=True, slots=False)
    class Comment:
        can_create: str = "comments:create"
        can_update: str = "comments:update"
        can_delete: str = "comments:delete"
        can_view: str = "comments:view"

    @dataclasses.dataclass(frozen=True, slots=False)
    class User:
        can_view: str = "users:view"
        can_view_list: str = "users:view_list"

    @dataclasses.dataclass(frozen=True, slots=False)
    class UserSettings:
        can_update: str = "user_settings:update"


class AbstractObjectPermission(ABC):

    @staticmethod
    @abstractmethod
    def get_object_lvl_permission(model_object: AbstractModel) -> list[Tuple[str, list[str]]]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        raise NotImplementedError
