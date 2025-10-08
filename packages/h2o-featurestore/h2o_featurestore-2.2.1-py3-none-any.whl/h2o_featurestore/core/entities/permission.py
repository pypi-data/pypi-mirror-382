
from h2o_featurestore.gen.model.v1_revoke_permission_request import (
    V1RevokePermissionRequest,
)

from .permission_base import PermissionBase
from .user import User


class Permission(PermissionBase):
    @property
    def user(self):
        return User(self._permission.user)


class ManageablePermission(Permission):
    @property
    def requestor(self):
        return User(self._permission.user)

    def revoke(self, reason):
        """Revoke permission.

        A particular permission can be revoked.

        Args:
            reason: (str) A reason for revoke.

        Typical example:
            manageable_permission.revoke("user left the project")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = V1RevokePermissionRequest(permission_id=self._permission.id, reason=reason)
        self._stub.core_service_revoke_permission(body=request)
