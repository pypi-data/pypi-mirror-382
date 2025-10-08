from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_permission_state import V1PermissionState

from .entities.permission import ManageablePermission
from .entities.permission import Permission
from .entities.permission_request import ManageablePermissionRequest
from .entities.permission_request import PermissionRequest


class AccessControlList:
    def __init__(self, stub: CoreServiceApi, online_stub):
        self.requests = AclRequests(stub, online_stub)
        self.permissions = AclPermissions(stub, online_stub)


class AclRequests:
    def __init__(self, stub, online_stub):
        self.projects = AclProjectRequests(stub, online_stub)
        self.feature_sets = AclFeatureSetsRequests(stub, online_stub)


class AclPermissions:
    def __init__(self, stub, online_stub):
        self.projects = AclProjectPermissions(stub, online_stub)
        self.feature_sets = AclFeatureSetsPermissions(stub, online_stub)


class AclProjectRequests:
    def __init__(self, stub: CoreServiceApi, online_stub):
        self._stub = stub
        self._online_stub = online_stub

    def list(self):
        """List pending project permission requests.

        Returns:
            Generator of project permission requests

        Typical example:
            my_requests = client.acl.requests.projects.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """

        args = {
            "filters": [str(V1PermissionState("PENDING"))],
            "page_token": "",
        }
        return (
            PermissionRequest(self._stub, self._online_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_project_permissions_page)
        )

    def list_manageable(self):
        """List pending manageable project permission requests.

        Returns:
            Generator of manageable project permission requests

        Typical example:
            manageable_requests = client.acl.requests.projects.list_manageable()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        args = {
            "filters": [str(V1PermissionState("PENDING"))],
            "page_token": "",
        }
        return (
            ManageablePermissionRequest(self._stub, self._online_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_manageable_project_permissions_page)
        )


class AclFeatureSetsRequests:
    def __init__(self, stub: CoreServiceApi, online_stub):
        self._stub = stub
        self._online_stub = online_stub

    def list(self):
        """List pending feature set permission requests.

        Returns:
            Generator of feature set permission requests

        Typical example:
            my_requests = client.acl.requests.feature_sets.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        args = {
            "filters": [str(V1PermissionState("PENDING"))],
            "page_token": "",
        }
        return (
            PermissionRequest(self._stub, self._online_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_feature_sets_permissions_page)
        )

    def list_manageable(self):
        """List pending manageable feature set permission requests.

        Returns:
            Generator of manageable feature set permission requests

        Typical example:
            manageable_requests = client.acl.requests.feature_sets.list_manageable()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        args = {
            "filters": [str(V1PermissionState("PENDING"))],
            "page_token": "",
        }

        return (
            ManageablePermissionRequest(self._stub, self._online_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_manageable_feature_sets_permissions_page)
        )


class AclProjectPermissions:
    def __init__(self, stub: CoreServiceApi, online_stub):
        self._stub = stub
        self._online_stub = online_stub

    def list(self, filters=None):
        """List existing project permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of project permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            my_requests = client.acl.requests.projects.list(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#requesting-permissions-to-a-project
        """
        args = {
            "filters": [str(V1PermissionState("GRANTED"))],
            "page_token": "",
        }
        if filters:
            args["filters"] = [str(f) for f in filters]
        return (
            Permission(self._stub, self._online_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_project_permissions_page)
        )

    def list_manageable(self, filters=None):
        """List pending manageable project permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of manageable project permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            manageable_requests = client.acl.requests.projects.list_manageable(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        args = {
            "filters": [str(V1PermissionState("GRANTED"))],
            "page_token": "",
        }
        if filters:
            args["filters"] = [str(f) for f in filters]
        return (
            ManageablePermission(self._stub, self._online_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_manageable_project_permissions_page)
        )


class AclFeatureSetsPermissions:
    def __init__(self, stub, online_stub):
        self._stub = stub
        self._online_stub = online_stub

    def list(self, filters=None):
        """List pending feature set permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of feature set permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            my_requests = client.acl.requests.feature_sets.list(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-feature-set-permissions
        """
        args = {
            "filters": [str(V1PermissionState("GRANTED"))],
            "page_token": "",
        }
        if filters:
            args["filters"] = [str(f) for f in filters]

        return (
            Permission(self._stub, self._online_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_feature_sets_permissions_page)
        )

    def list_manageable(self, filters=None):
        """List pending manageable feature set permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of manageable feature set permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            manageable_requests = client.acl.requests.feature_sets.list_manageable(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-feature-set-permissions
        """
        args = {
            "filters": [str(V1PermissionState("GRANTED"))],
            "page_token": "",
        }
        if filters:
            args["filters"] = [str(f) for f in filters]
        return (
            ManageablePermission(self._stub, self._online_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(args, self._stub.core_service_list_manageable_feature_sets_permissions_page)
        )

def paged_response_to_request(args, core_call):
    while args:
        response = core_call(**args)
        if response.next_page_token:
            args["page_token"] = response.next_page_token
        else:
            args = None
        for entry in response.entries:
            yield entry
