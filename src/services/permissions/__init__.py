from typing import Type

from db.models import CommentModel, PostModel, UserModel

from services.errors import PermissionDeniedError
from services.permissions.base import AbstractModel, AbstractObjectPermission
from services.permissions.comments import CommentPermissions
from services.permissions.posts import PostPermissions
from services.permissions.users import UserPermission

__all__ = [
    "check_object_permission",
    "check_operation_permission",
]

OBJECT_PERMISSION_TABLE = {
    PostModel.__tablename__: PostPermissions,
    CommentModel.__tablename__: CommentPermissions,
    UserModel.__tablename__: UserPermission,
}


def check_object_permission(
        operation: str,
        user: UserModel,
        item: AbstractModel,
):
    object_permission_class: Type[AbstractObjectPermission] = OBJECT_PERMISSION_TABLE.get(item.__tablename__)
    object_permission = object_permission_class.get_object_lvl_permission(item)
    for permission in object_permission:
        if operation == permission[0]:
            allowed_roles = permission[1]
            if "all" in allowed_roles or user.role in allowed_roles or user.id in allowed_roles:
                return
    raise PermissionDeniedError


def check_operation_permission(
        operation: str,
        user: UserModel,
):
    model_name = operation.split(":")[0]
    object_permission_class: Type[AbstractObjectPermission] = OBJECT_PERMISSION_TABLE.get(model_name)
    operation_permission = object_permission_class.get_operation_lvl_permission()
    for permission in operation_permission:
        if operation == permission[0]:
            allowed_roles = permission[1]
            if "all" in allowed_roles or user.role.value in allowed_roles:
                return
    raise PermissionDeniedError
