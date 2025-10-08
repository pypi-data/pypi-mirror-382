from typing import Iterator

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi

from .entities.feature_set_popularity import FeatureSetPopularity
from .entities.pinned_feature_set import PinnedFeatureSet
from .entities.recently_used_feature_set import RecentlyUsedFeatureSet
from .entities.recently_used_project import RecentlyUsedProject


class Dashboard:
    def __init__(self, stub: CoreServiceApi, online_stub):
        self._stub = stub
        self._online_stub = online_stub

    def get_feature_sets_popularity(self):
        """Get popular feature sets.

        Returns:
            List of feature sets popularity

        Typical example:
            fs_popularity = client.dashboard.get_feature_sets_popularity()
        """
        response = self._stub.core_service_get_feature_sets_popularity()
        return [
            FeatureSetPopularity(self._stub, self._online_stub, popular_feature_set)
            for popular_feature_set in response.feature_sets
        ]

    def get_recently_used_projects(self):
        """Get projects that were recently utilized.

        Returns:
            List of references to projects

        Typical example:
            recently_used_projects = client.dashboard.get_recently_used_projects()
        """
        response = self._stub.core_service_get_recently_used_projects()
        return [RecentlyUsedProject(self._stub, self._online_stub, project) for project in response.projects]

    def get_recently_used_feature_sets(self):
        """Get feature sets that were recently utilized.

        Returns:
            List of references to feature sets

        Typical example:
            recently_used_feature_sets = client.dashboard.get_recently_used_feature_sets()
        """
        response = self._stub.core_service_get_recently_used_feature_sets()
        return [
            RecentlyUsedFeatureSet(self._stub, self._online_stub, feature_set) for feature_set in response.feature_sets
        ]

    def list_pinned_feature_sets(self) -> Iterator[PinnedFeatureSet]:
        """List feature sets that were pinned by current user.

        Returns:
            Iterator[PinnedFeatureSet]: An iterator which obtains the pinned feature sets lazily.

        Typical example:
            client.dashboard.list_pinned_feature_sets()
        """
        args = {
            "page_token": "",
        }
        while args:
            response = self._stub.core_service_list_pinned_feature_sets(**args)
            if response.next_page_token:
                args["page_token"] = response.next_page_token
            else:
                args = {}
            for feature_set in response.feature_sets:
                yield PinnedFeatureSet(self._stub, self._online_stub, feature_set)
