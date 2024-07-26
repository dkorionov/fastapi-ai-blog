import dataclasses
import enum
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Tuple

from core.config.constansts import UserRole

from domains.dto import AbstractDTO, PostDTO, UserDTO

__all__ = [
    "get_permission_table"
]

from domains.dto.comment import FullCommentDTO


class PermissionRoles(enum.Enum):
    admin: str = UserRole.ADMIN.value
    user: str = UserRole.USER.value
    all: str = "all"


@dataclasses.dataclass(frozen=True, slots=False)
class OperationPermission:
    @dataclasses.dataclass(frozen=True, slots=False)
    class Post:
        can_create: str = "post:create"
        can_update: str = "post:update"
        can_delete: str = "post:delete"
        can_view: str = "post:view"
        can_view_list: str = "post:view_list"

    @dataclasses.dataclass(frozen=True, slots=False)
    class Comment:
        can_create: str = "comment:create"
        can_update: str = "comment:update"
        can_delete: str = "comment:delete"
        can_view: str = "comment:view"

    @dataclasses.dataclass(frozen=True, slots=False)
    class User:
        can_view: str = "user:view"
        can_view_list: str = "user:view_list"

    @dataclasses.dataclass(frozen=True, slots=False)
    class UserSettings:
        can_update: str = "user_settings:update"


class AbstractObjectPermission(ABC):

    @staticmethod
    @abstractmethod
    def get_object_lvl_permission(model_object: AbstractDTO) -> list[Tuple[str, list[str]]]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        raise NotImplementedError


class PostPermissions(AbstractObjectPermission):

    @staticmethod
    def get_object_lvl_permission(model_object: PostDTO) -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Post.can_update, [model_object.author_id]),
            (OperationPermission.Post.can_delete, [PermissionRoles.admin.value, model_object.author_id]),
            (OperationPermission.Post.can_view, [PermissionRoles.all.value]),
        ]

    @staticmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Post.can_create, [PermissionRoles.all.value]),
            (OperationPermission.Post.can_view_list, [PermissionRoles.all.value]),
        ]


class CommentPermissions(AbstractObjectPermission):

    @staticmethod
    def get_object_lvl_permission(model_object: FullCommentDTO) -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Comment.can_update, [model_object.author_id]),
            (OperationPermission.Comment.can_delete, [
                PermissionRoles.admin.value,
                model_object.author_id,
                model_object.post.author_id
            ]),
            (OperationPermission.Comment.can_view, [PermissionRoles.all.value]),
        ]

    @staticmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        return [
            (OperationPermission.Comment.can_create, [PermissionRoles.all.value]),
        ]


class UserPermission(AbstractObjectPermission):

    @staticmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        return [(OperationPermission.User.can_view_list, [PermissionRoles.admin.value])]

    @staticmethod
    def get_object_lvl_permission(model_object: UserDTO) -> list[Tuple[str, list[str]]]:
        return []


OBJECT_PERMISSION_TABLE = {
    "post": PostPermissions,
    "comment": CommentPermissions,
    "user": UserPermission,
}


@lru_cache(maxsize=1)
def get_permission_table():
    return OBJECT_PERMISSION_TABLE
