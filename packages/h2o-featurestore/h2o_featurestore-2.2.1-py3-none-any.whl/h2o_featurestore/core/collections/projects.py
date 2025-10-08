import logging
from typing import Iterator
from typing import Optional

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.apis import OnlineServiceApi
from h2o_featurestore.gen.model.v1_create_project_request import V1CreateProjectRequest

from ..access_modifier import AccessModifier
from ..entities.feature_set import FeatureSet
from ..entities.project import Project
from .admin_projects import AdminProjects


class Projects:
    def __init__(self, stub: CoreServiceApi, online_stub: OnlineServiceApi, admin_projects: AdminProjects):
        self._stub = stub
        self._online_stub = online_stub
        self.admin_projects = admin_projects

    def list(self) -> Iterator[Project]:
        """List all available projects.

        Returns:
            Generator of all projects

        Typical example:
            client.projects.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/projects_api.html#listing-projects
        """
        has_next_page = True
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_projects_page(page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for project in response.projects:
                yield Project.from_listable_project(self._stub, self._online_stub, project)

    def list_feature_sets(self, project_names=[]) -> Iterator[FeatureSet]:
        """List feature sets across multiple projects.

        Args:
            project_names: (list[str]) A collection of existing project names.

        Returns:
            Iterator[FeatureSet]: An iterator which obtains the feature sets lazily.

        Typical example:
            client.projects.list_feature_sets(["project_name_A", "project_name_B"])

        For more details:
            https://docs.h2o.ai/featurestore/api/projects_api.html#listing-feature-sets-across-multiple-projects
        """
        has_next_page = True
        page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_feature_sets_page(
                project_names=project_names,
                page_token=page_token
            )
            if response.next_page_token:
                page_token = response.next_page_token
            else:
                has_next_page = False
            for feature_set in response.feature_sets:
                yield FeatureSet(self._stub, self._online_stub, feature_set)

    def create(self, project_name: str, description: str = "", access_modifier: Optional[AccessModifier] = None) -> Project:
        """Create a project.

        Args:
            project_name: (str) A project name.
            description: (str) A description about the project.
            access_modifier: (AccessModifier) If AccessModifier.PUBLIC, project is visible to all users
                                              If AccessModifier.PROJECT_ONLY, only users with viewer permission can list
                                              feature sets within this project.
                                              If AccessModifier.PRIVATE, project is visible only to its owner.

        Returns:
            Project: A new project with specified attributes.

        Typical example:
            project = client.projects.create(project_name="project", description="description",
              access_type=AccessModifier.PUBLIC)

        For more details:
            https://docs.h2o.ai/featurestore/api/projects_api.html#create-a-project
        """
        request = V1CreateProjectRequest()
        request.access_modifier = AccessModifier.to_proto(access_modifier)
        request.project_name = project_name
        request.description = description
        response = self._stub.core_service_create_project(body=request)
        if response.already_exists:
            logging.warning("Project '" + project_name + "' already exists.")
        return Project(self._stub, self._online_stub, response.project)


    def get(self, project_id: str) -> Project:
        """Obtain an existing project.

        Args:
            project_id: (str) A project ID.

        Returns:
            Project: An existing project.

        Typical example:
            project = client.projects.get(project_id="project_id")
        """
        response = self._stub.core_service_get_project_by_id(project_id=project_id)
        return Project(self._stub, self._online_stub, response.project)

    def get_by_name(self, project_name: str) -> Project:
        """Get a project by name.

        Args:
            name: (str) A project name.

        Returns:
            Project: The project if found, otherwise None.

        Typical example:
            project = client.projects.get_by_name(project_name="project_name")
        """
        response = self._stub.core_service_search_projects(query=project_name, page_size=1)
        if response.listable_project:
            for project in response.listable_project:
                if project.name == project_name:
                    return Project.from_listable_project(self._stub, self._online_stub, project)
        raise Exception(f"Project '{project_name}' not found.")

    def __repr__(self):
        return "This class wraps together methods working with projects"
