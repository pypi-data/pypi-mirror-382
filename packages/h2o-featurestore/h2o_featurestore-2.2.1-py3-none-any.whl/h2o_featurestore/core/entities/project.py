import logging
import time

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.api.online_service_api import OnlineServiceApi
from h2o_featurestore.gen.model.core_service_add_project_permission_body import (
    CoreServiceAddProjectPermissionBody,
)
from h2o_featurestore.gen.model.core_service_remove_project_permission_body import (
    CoreServiceRemoveProjectPermissionBody,
)
from h2o_featurestore.gen.model.core_service_submit_pending_project_permission_body import (
    CoreServiceSubmitPendingProjectPermissionBody,
)
from h2o_featurestore.gen.model.core_service_update_project_body import (
    CoreServiceUpdateProjectBody,
)
from h2o_featurestore.gen.model.v1_listable_project import V1ListableProject
from h2o_featurestore.gen.model.v1_permission_type import V1PermissionType
from h2o_featurestore.gen.model.v1_project import V1Project
from h2o_featurestore.gen.model.v1_updatable_project_field import (
    V1UpdatableProjectField,
)

from ..access_modifier import AccessModifier
from ..access_type import AccessType
from ..browser import Browser
from ..collections.feature_set_reviews import FeatureSetReviews
from ..collections.feature_sets import FeatureSets
from ..utils import Utils
from .project_history import ProjectHistory
from .user import User
from .user_with_permission import UserWithPermission


class Project:
    def __init__(self, stub: CoreServiceApi, online_stub: OnlineServiceApi, project: V1Project):
        self._project = project
        self._stub = stub
        self._online_stub = online_stub
        self.feature_sets = FeatureSets(stub, self._online_stub, project)
        self.feature_set_reviews = FeatureSetReviews(stub, self._online_stub, project.id)

    @classmethod
    def from_listable_project(cls, stub: CoreServiceApi, online_stub: OnlineServiceApi, listable_project: V1ListableProject):
        project = V1Project(name=listable_project.name,
            description=listable_project.description,
            author=listable_project.author,
            last_update_date_time=listable_project.last_update_date_time,
            id=listable_project.id,
            feature_sets_count=listable_project.feature_sets_count,
            access_modifier=listable_project.access_modifier,
        )
        return cls(stub, online_stub, project)

    @property
    def id(self):
        return self._project.id

    @property
    def name(self):
        return self._project.name

    @property
    def description(self):
        return self._project.description

    @description.setter
    def description(self, value):
        request = CoreServiceUpdateProjectBody(
            description=value,
            fields_to_update=[V1UpdatableProjectField("PROJECT_DESCRIPTION")]
        )
        self._project = self._stub.core_service_update_project(self._project.id, body=request).updated_project

    @property
    def access_modifier(self):
        return AccessModifier.from_proto(self._project.access_modifier).name

    @access_modifier.setter
    def access_modifier(self, value):
        request = CoreServiceUpdateProjectBody(
            access_modifier=AccessModifier.to_proto(value),
            fields_to_update=[V1UpdatableProjectField("PROJECT_ACCESS_MODIFIER")],
        )
        self._project = self._stub.core_service_update_project(self._project.id, body=request).updated_project

    @property
    def author(self):
        return User(self._project.author)

    @property
    def custom_data(self):
        return self._project.custom_data

    @custom_data.setter
    def custom_data(self, value):
        request = CoreServiceUpdateProjectBody(
            custom_data=value,
            fields_to_update=[V1UpdatableProjectField("PROJECT_CUSTOM_DATA")],
        )
        self._project = self._stub.core_service_update_project(self._project.id, body=request).updated_project

    def delete(self, wait_for_completion=False):
        """Deletes the project."""
        self._stub.core_service_delete_project(self._project.id)
        if wait_for_completion:
            while self._stub.core_service_project_exists(self._project.id).exists:
                time.sleep(1)
                logging.debug(f"Waiting for project '{self._project.name}' deletion...")
        logging.info(f"Project '{self._project.name}' is deleted")

    def add_owners(self, user_emails):
        """Add additional owner/owners to project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.add_owners(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Owner"))

    def add_editors(self, user_emails):
        """Add additional editor/editors to project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.add_editors(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Editor"))

    def add_consumers(self, user_emails):
        """Add additional consumer/consumers to project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.add_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Consumer"))

    def add_sensitive_consumers(self, user_emails):
        """Add additional sensitive consumer/consumers to project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.add_sensitive_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._add_permissions(user_emails, V1PermissionType("SensitiveConsumer"))

    def add_viewers(self, user_emails):
        """Add additional viewer/viewers to project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.add_viewers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Viewer"))

    def remove_owners(self, user_emails):
        """Remove owner/owners from project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.remove_owners(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Owner"))

    def remove_editors(self, user_emails):
        """Remove editor/editors from project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.remove_editors(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Editor"))

    def remove_consumers(self, user_emails):
        """Remove consumer/consumers from project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.remove_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Consumer"))

    def remove_sensitive_consumers(self, user_emails):
        """Remove sensitive consumer/consumers from project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.remove_sensitive_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("SensitiveConsumer"))

    def remove_viewers(self, user_emails):
        """Remove viewer/viewers from project.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            Project: An existing project with the latest information.

        Typical example:
            project.remove_viewers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#project-permission-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Viewer"))

    def list_owners(self):
        return self._list_users(V1PermissionType("Owner"))

    def list_editors(self):
        return self._list_users(V1PermissionType("Editor"))

    def list_consumers(self):
        return self._list_users(V1PermissionType("Consumer"))

    def list_sensitive_consumers(self):
        return self._list_users(V1PermissionType("SensitiveConsumer"))

    def list_viewers(self):
        return self._list_users(V1PermissionType("Viewer"))

    def _list_users(self, permission: V1PermissionType):
        has_next_page = True
        page_size = 100
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_get_user_project_permissions(
                resource_id=self.id,
                page_size=page_size,
                page_token=next_page_token,
                permission_filter=str(permission))
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for user_with_permissions in response.users:
                yield UserWithPermission(user_with_permissions)

    def _add_permissions(self, user_emails, permission):
        request = CoreServiceAddProjectPermissionBody()
        request.user_emails = user_emails if isinstance(user_emails, list) else [user_emails]
        request.permission = permission
        self._stub.core_service_add_project_permission(self.id, request)
        return self

    def _remove_permissions(self, user_emails, permission):
        request = CoreServiceRemoveProjectPermissionBody()
        request.user_emails = user_emails if isinstance(user_emails, list) else [user_emails]
        request.permission = permission
        self._stub.core_service_remove_project_permission(self.id, body=request)
        return self

    def request_access(self, access_type, reason):
        """Request project permissions.

        Args:
            access_type: (PermissionType) Object represents type of permission.
                OWNER | EDITOR | CONSUMER | SENSITIVE_CONSUMER
            reason: (str) A reason for permission request.

        Returns:
            str: A permission id.

        Typical example:
            my_request_id = project.request_access(AccessType.CONSUMER, "Preparing the best model")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#requesting-permissions-to-a-project
        """
        request = CoreServiceSubmitPendingProjectPermissionBody()
        request.permission = AccessType.to_proto_permission(access_type)
        request.reason = reason
        response = self._stub.core_service_submit_pending_project_permission(self._project.id,
                                                                             body=request)
        return response.permission_id

    @property
    def current_permission(self):
        """Lists current access rights."""
        response = self._stub.core_service_get_active_project_permission(self._project.id)
        return AccessType.from_proto_active_permission(response.permission)

    @property
    def history(self):
        """Lists changes that were applied to this project."""
        next_page_token = ""
        has_next_page = True
        while has_next_page:
            response = self._stub.core_service_list_project_history_page(project_id=self._project.id, next_page_token=next_page_token)
            if response.next_page_token:
                 next_page_token = response.next_page_token
            else:
                has_next_page = False
            for history_record in response.history:
                yield ProjectHistory(self._stub, self._online_stub, history_record)

    @property
    def created_date_time(self):
        return Utils.timestamp_to_string(self._project.created_date_time)

    @property
    def last_updated_date_time(self):
        return Utils.timestamp_to_string(self._project.last_update_date_time)

    @property
    def last_updated_by(self):
        return User(self._project.last_updated_by)

    def open_website(self):
        page = f"/project/{self.id}"
        Browser(self._stub).open_website(page)

    def __repr__(self):
        return Utils.pretty_print_proto(self._project)

    def __str__(self):
        return (
            f"Project name    : {self.name} \n"
            f"Description     : {self.description} \n"
            f"Access modifier : {self.access_modifier} \n"
            f"Author            \n{Utils.output_indent_spacing(str(self.author), '  ')}"
            f"Created         : {Utils.proto_to_dict(self._project).get('created_date_time')} \n"
            f"Last updated    : {Utils.proto_to_dict(self._project).get('last_update_date_time')} \n"
            f"Last updated by   \n{Utils.output_indent_spacing(str(self.last_updated_by), '  ')}"
        )