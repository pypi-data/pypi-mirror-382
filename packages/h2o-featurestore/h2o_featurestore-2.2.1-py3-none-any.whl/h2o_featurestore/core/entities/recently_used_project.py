
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi

from ..utils import Utils
from .project import Project


class RecentlyUsedProject:
    def __init__(self, stub: CoreServiceApi, online_stub, recently_used_project):
        self._stub = stub
        self._online_stub = online_stub
        self._recently_used_project = recently_used_project

    @property
    def name(self):
        return self._recently_used_project.project_name

    @property
    def description(self):
        return self._recently_used_project.project_description

    @property
    def updated_at(self):
        return Utils.timestamp_to_string(self._recently_used_project.updated_at)

    @property
    def last_access_at(self):
        return Utils.timestamp_to_string(self._recently_used_project.last_access_at)

    def get_project(self):
        response = self._stub.core_service_get_project_by_id(project_id=self._recently_used_project.project_id)
        return Project(self._stub, self._online_stub, response.project)

    def __repr__(self):
        return Utils.pretty_print_proto(self._recently_used_project)
