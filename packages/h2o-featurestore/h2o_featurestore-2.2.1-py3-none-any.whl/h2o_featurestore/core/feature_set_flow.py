from enum import Enum

from h2o_featurestore.gen.model.v1_feature_set_flow import V1FeatureSetFlow


class FeatureSetFlow(Enum):
    ONLINE_ONLY =  "ONLINE_ONLY"
    OFFLINE_ONLY = "OFFLINE_ONLY"
    OFFLINE_ONLINE_MANUAL = "OFFLINE_ONLINE_MANUAL"
    OFFLINE_ONLINE_AUTOMATIC = "OFFLINE_ONLINE_AUTOMATIC"

    @staticmethod
    def _from_proto(flow: V1FeatureSetFlow):
        return FeatureSetFlow(str(flow))
