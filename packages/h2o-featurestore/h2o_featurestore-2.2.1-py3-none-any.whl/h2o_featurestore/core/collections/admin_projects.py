from typing import Iterator

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.api.online_service_api import OnlineServiceApi

from ..access_type import AccessType
from ..entities.project import Project


class AdminProjects:
    def __init__(self, stub: CoreServiceApi, online_stub: OnlineServiceApi):
        self._stub = stub
        self._online_stub = online_stub

    def list(self, user_email: str, required_permission: AccessType) -> Iterator[Project]:
        """List all available projects as an administrator.

        Args:
            user_email: (str) A User email to search projects for
            required_permission: (AccessType) The required permission to list projects.
                If None, all projects are returned regardless of permissions.

        Returns:
            Generator of all projects

        Typical example:
            client.projects.list(user_email="bob@h2o.ai", required_permission=AccessType.OWNER)

        For more details:
            https://docs.h2o.ai/featurestore/api/admin_api.html#listing-projects
        """
        has_next_page = True
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_admin_search_projects(user_email=user_email, required_permission=required_permission, page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for project in response.listable_project:
                yield Project(self._stub, self._online_stub, project)
