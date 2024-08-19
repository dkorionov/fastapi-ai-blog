from typing import Tuple

from db.models import UserModel

from services.permissions.base import (
    AbstractObjectPermission,
    OperationPermission,
    PermissionRoles,
)


class UserPermission(AbstractObjectPermission):

    @staticmethod
    def get_operation_lvl_permission() -> list[Tuple[str, list[str]]]:
        return [(OperationPermission.User.can_view_list, [PermissionRoles.admin.value])]

    @staticmethod
    def get_object_lvl_permission(model_object: UserModel) -> list[Tuple[str, list[str]]]:
        return []
