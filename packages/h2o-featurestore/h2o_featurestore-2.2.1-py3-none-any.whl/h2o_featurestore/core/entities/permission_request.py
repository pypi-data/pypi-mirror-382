

from h2o_featurestore.gen.model.v1_approve_pending_permission_request import (
    V1ApprovePendingPermissionRequest,
)
from h2o_featurestore.gen.model.v1_reject_pending_permission_request import (
    V1RejectPendingPermissionRequest,
)
from h2o_featurestore.gen.model.v1_withdraw_pending_permission_request import (
    V1WithdrawPendingPermissionRequest,
)

from .permission_base import PermissionBase
from .user import User


class PermissionRequest(PermissionBase):
    @property
    def user(self):
        return User(self._permission.user)

    def withdraw(self):
        """Withdraw a previously raised permission request.

        Typical example:
            request.withdraw()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.htm
        """
        request = V1WithdrawPendingPermissionRequest(permission_id=self._permission.id)
        self._stub.core_service_withdraw_pending_permission(body=request)


class ManageablePermissionRequest(PermissionRequest):
    @property
    def requestor(self):
        """User who raised the specific permission request."""
        return User(self._permission.user)

    def approve(self, reason):
        """Approve a permission request.

        Args:
            reason: (str) A reason for permission request approval.

        Typical example:
            manageable_request.approve("it will be fun")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = V1ApprovePendingPermissionRequest(permission_id=self._permission.id, reason=reason)
        self._stub.core_service_approve_pending_permission(body=request)

    def reject(self, reason):
        """Reject a permission request.

        Args:
            reason: (str) A reason for permission request rejection.

        Typical example:
            manageable_request.reject("it's not ready yet")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = V1RejectPendingPermissionRequest(permission_id=self._permission.id, reason=reason)
        self._stub.core_service_reject_pending_permission(body=request)
