
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi

from ..access_type import AccessType
from ..utils import Utils
from .feature_set import FeatureSet


class FeatureSetPopularity:
    def __init__(self, stub: CoreServiceApi, online_stub, popular_feature_set):
        self._stub = stub
        self._online_stub = online_stub
        self._popular_feature_set = popular_feature_set

    @property
    def name(self):
        return self._popular_feature_set.feature_set_name

    @property
    def description(self):
        return self._popular_feature_set.feature_set_description

    @property
    def number_of_retrievals(self):
        return self._popular_feature_set.number_of_retrievals

    @property
    def current_permission(self):
        return AccessType.from_proto_active_permission(self._popular_feature_set.permission)

    def get_feature_set(self):
        response = self._stub.core_service_get_feature_set_by_id(feature_set_id=self._popular_feature_set.feature_set_id)
        return FeatureSet(self._stub, self._online_stub, response.feature_set)

    def __repr__(self):
        return Utils.pretty_print_proto(self._popular_feature_set)
