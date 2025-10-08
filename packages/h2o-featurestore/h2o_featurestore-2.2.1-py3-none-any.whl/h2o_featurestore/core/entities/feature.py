from __future__ import annotations

import json
from enum import Enum
from typing import TYPE_CHECKING

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.core_service_update_feature_body import (
    CoreServiceUpdateFeatureBody,
)
from h2o_featurestore.gen.model.v1_feature import V1Feature
from h2o_featurestore.gen.model.v1_feature_type import V1FeatureType
from h2o_featurestore.gen.model.v1_updatable_feature_field import (
    V1UpdatableFeatureField,
)

from ..commons.case_insensitive_dict import CaseInsensitiveDict
from ..utils import Utils
from .feature_ref import FeatureRef

if TYPE_CHECKING:  # Only imports the below statements during type checking
    from .feature_set import FeatureSet

class FeatureType(Enum):
    CATEGORICAL = "CATEGORICAL"
    NUMERICAL = "NUMERICAL"
    TEMPORAL = "TEMPORAL"
    TEXT = "TEXT"
    COMPOSITE = "COMPOSITE"
    AUTOMATIC_DISCOVERY = "AUTOMATIC_DISCOVERY"

    @classmethod
    def from_proto(cls, proto: V1FeatureType):
        return cls(str(proto))

    @classmethod
    def to_proto(cls, feature_type: FeatureType):
        return V1FeatureType(feature_type.value)

class Feature:
    def __init__(
        self, stub: CoreServiceApi, feature_set: FeatureSet, internal_feature: V1Feature, absolute_feature_name, escaped_absolute_feature_name
    ):
        self._stub = stub
        self._fs = feature_set
        self._internal_feature = internal_feature
        self._absolute_feature_name = absolute_feature_name
        self._escaped_absolute_feature_name = escaped_absolute_feature_name

    @property
    def name(self):
        return self._internal_feature.name

    @property
    def version(self):
        return self._internal_feature.version

    @property
    def special(self):
        return self._internal_feature.special

    @special.setter
    def special(self, value):
        update_request = CoreServiceUpdateFeatureBody(
            special=value,
            feature_set_version=self._fs.version,
            fields_to_update=[V1UpdatableFeatureField("FEATURE_SPECIAL")]
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._internal_feature.id, body=update_request)
        self._fs._feature_set = response.updated_feature_set
        self._internal_feature = response.updated_feature

    @property
    def version_change(self):
        return self._internal_feature.version_change

    @property
    def status(self):
        return self._internal_feature.status

    @status.setter
    def status(self, value):
        update_request = V1UpdatableFeatureField(
            feature_set_version=self._fs.version,
            status=value,
            fields_to_update=[V1UpdatableFeatureField("FEATURE_STATUS")],
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._internal_feature.id, body=update_request)
        self._fs._feature_set = response.updated_feature_set
        self._internal_feature = response.updated_feature

    @property
    def data_type(self):
        return self._internal_feature.data_type

    @property
    def profile(self):
        return FeatureProfile(self._stub, self._fs, self)

    @property
    def description(self):
        return self._internal_feature.description

    @description.setter
    def description(self, value):
        update_request = CoreServiceUpdateFeatureBody(
            description=value,
            feature_set_version=self._fs.version,
            fields_to_update=[V1UpdatableFeatureField("FEATURE_DESCRIPTION")]
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._internal_feature.id, body=update_request)
        self._fs._feature_set = response.updated_feature_set
        self._internal_feature = response.updated_feature

    @property
    def classifiers(self):
        return set(self._internal_feature.classifiers)

    @classifiers.setter
    def classifiers(self, value: set):
        update_request = CoreServiceUpdateFeatureBody(
            feature_set_version=self._fs.version,
            classifiers=list(value)[:],
            fields_to_update=[V1UpdatableFeatureField("FEATURE_CLASSIFIERS")]
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._internal_feature.id, body=update_request)
        self._fs._feature_set = response.updated_feature_set
        self._internal_feature = response.updated_feature

    @property
    def importance(self):
        return self._internal_feature.importance

    @importance.setter
    def importance(self, value):
        update_request = CoreServiceUpdateFeatureBody(
            importance=value,
            feature_set_version=self._fs.version,
            fields_to_update=[V1UpdatableFeatureField("FEATURE_IMPORTANCE")]
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._internal_feature.id, body=update_request)
        self._fs._feature_set = response.updated_feature_set
        self._internal_feature = response.updated_feature

    @property
    def monitoring(self) -> Monitoring:
        return Monitoring(self._stub, self._fs, self)

    @property
    def special_data(self) -> FeatureSpecialData:
        return FeatureSpecialData(self)

    @property
    def custom_data(self):
        return self._internal_feature.custom_data

    @custom_data.setter
    def custom_data(self, value):
        update_request = CoreServiceUpdateFeatureBody(
            custom_data=value,
            feature_set_version=self._fs.version,
            fields_to_update=[V1UpdatableFeatureField("FEATURE_CUSTOM_DATA")],
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._internal_feature.id, body=update_request)
        self._fs._feature_set = response.updated_feature_set
        self._internal_feature = response.updated_feature

    @property
    def nested_features(self):
        return CaseInsensitiveDict(
            {
                feature.name: Feature(
                    self._stub,
                    self._fs,
                    feature,
                    self._absolute_feature_name + "." + feature.name,
                    (
                        self._escaped_absolute_feature_name + f".`{feature.name}`"
                        if "." in feature.name
                        else self._escaped_absolute_feature_name + f".{feature.name}"
                    ),
                )
                for feature in self._internal_feature.nested_features
            }
        )

    def mark_as_target_variable(self):
        self._stub.core_service_mark_feature_as_target(
            feature_set_id=self._fs.id,
            feature_set_version=self._fs.version,
            feature_id=self._internal_feature.id,
        )

    def discard_as_target_variable(self):
        self._stub.core_service_discard_feature_as_target(
            feature_set_id=self._fs.id,
            feature_set_version=self._fs.version,
            feature_id=self._internal_feature.id,
        )

    def _reference(self) -> FeatureRef:
        return FeatureRef(self._escaped_absolute_feature_name, self._fs._reference())

    def __repr__(self):
        return Utils.pretty_print_proto(self._internal_feature)

    def __str__(self):
        return (
            f"Feature name      : {self.name} \n"
            f"Description       : {self.description} \n"
            f"Version           : {self.version} \n"
            f"Data type         : {self.data_type} \n"
            f"Sensitive         : {self.special_data.sensitive} \n"
            f"Nested features   : {self._custom_feature_fields()} \n"
            f"Classifiers       : {self.classifiers} \n"
        )

    def _custom_feature_fields(self):
        s = dict()
        for feature in self.nested_features:
            s.update({feature: self.nested_features.get(feature).data_type})
        return json.dumps(s, indent=5)


class FeatureProfile:
    def __init__(self, stub: CoreServiceApi, feature_set, feature: Feature):
        self._stub = stub
        self._fs = feature_set
        self._feature = feature

    @property
    def feature_type(self) -> FeatureType:
        return FeatureType.from_proto(self._feature._internal_feature.profile.feature_type)

    @feature_type.setter
    def feature_type(self, value: FeatureType):
        update_request = CoreServiceUpdateFeatureBody(
            feature_set_version=self._fs.version,
            type=FeatureType.to_proto(value),
            fields_to_update=[V1UpdatableFeatureField("FEATURE_TYPE")],
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._feature._internal_feature.id, body=update_request)
        self._feature._fs._feature_set = response.updated_feature_set
        self._feature._internal_feature = response.updated_feature

    @property
    def categorical_statistics(self):
        return CategoricalStatistics(self._feature._internal_feature.profile)

    @property
    def statistics(self):
        return FeatureStatistics(self._feature._internal_feature.profile)

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature._internal_feature.profile)

    def __str__(self):
        return (
            f"Feature type  : {self.feature_type} \n"
            f"Categorical     \n{Utils.output_indent_spacing(str(self.categorical_statistics), '    ')}"
            f"Statistics      \n{Utils.output_indent_spacing(str(self.statistics), '  ')}"
        )


class FeatureStatistics:
    def __init__(self, feature):
        self._feature = feature
        self._stats = self._feature.statistics

    @property
    def max(self):
        return self._stats.max

    @property
    def mean(self):
        return self._stats.mean

    @property
    def median(self):
        return self._stats.median

    @property
    def min(self):
        return self._stats.min

    @property
    def stddev(self):
        return self._stats.stddev

    @property
    def stddev_rec_count(self):
        return self._stats.stddev_rec_count

    @property
    def null_count(self):
        return self._stats.null_count

    @property
    def nan_count(self):
        return self._stats.nan_count

    @property
    def unique(self):
        return self._stats.unique

    def __repr__(self):
        return Utils.pretty_print_proto(self._stats)

    def __str__(self):
        return (
            f"Max                : {self.max} \n"
            f"Mean               : {self.mean} \n"
            f"Median             : {self.median} \n"
            f"Min                : {self.min} \n"
            f"Standard deviation : {self.stddev} \n"
            f"Records count      : {self.stddev_rec_count} \n"
            f"Null values count  : {self.null_count} \n"
            f"NaN values count   : {self.nan_count} \n"
            f"Unique             : {self.unique} \n"
        )


class CategoricalStatistics:
    def __init__(self, feature):
        self._feature = feature
        self._categorical = self._feature.categorical

    @property
    def unique(self):
        return self._categorical.unique

    @property
    def top(self):
        return [FeatureTop(top) for top in self._categorical.top]

    def __repr__(self):
        return Utils.pretty_print_proto(self._categorical)

    def __str__(self):
        return f"Unique    : {self.unique} \n" f"Top       : {self.top} \n"


class FeatureTop:
    def __init__(self, feature):
        self._feature = feature
        self._top = self._feature.top

    @property
    def name(self):
        return self._top.name

    @property
    def count(self):
        return self._top.count

    def __repr__(self):
        return Utils.pretty_print_proto(self._top)

    def __str__(self):
        return f"Name  : {self.name} \n" f"Count : {self.count} \n"


class Monitoring:
    def __init__(self, stub, feature_set, feature):
        self._stub = stub
        self._fs = feature_set
        self._feature = feature

    @property
    def anomaly_detection(self):
        return self._feature._internal_feature.monitoring.anomaly_detection

    @anomaly_detection.setter
    def anomaly_detection(self, value):
        update_request = CoreServiceUpdateFeatureBody(
            anomaly_detection=value,
            feature_set_version=self._fs.version,
            fields_to_update=[V1UpdatableFeatureField("FEATURE_ANOMALY_DETECTION")],
        )
        response = self._stub.core_service_update_feature(self._fs.id, self._feature._internal_feature.id, body=update_request)
        self._feature._fs._feature_set = response.updated_feature_set
        self._feature._internal_feature = response.updated_feature

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature._internal_feature.monitoring)

    def __str__(self):
        return f"Anomaly detection : {self.anomaly_detection} \n"


class FeatureSpecialData:
    def __init__(self, feature: Feature):
        self._feature = feature

    @property
    def spi(self):
        return self._feature._internal_feature.special_data.spi

    @property
    def pci(self):
        return self._feature._internal_feature.special_data.pci

    @property
    def rpi(self):
        return self._feature._internal_feature.special_data.rpi

    @property
    def demographic(self):
        return self._feature._internal_feature.special_data.demographic

    @property
    def sensitive(self):
        return self._feature._internal_feature.special_data.sensitive

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature._internal_feature.special_data)

    def __str__(self):
        if self.sensitive:
            return (
                f"spi          : {self.spi} \n"
                f"pci          : {self.pci} \n"
                f"rpi          : {self.rpi} \n"
                f"demographic  : {self.demographic} \n"
                f"sensitive    : {self.sensitive} \n"
            )
        return (
            f"spi          : *** \n"
            f"pci          : *** \n"
            f"rpi          : *** \n"
            f"demographic  : *** \n"
            f"sensitive    : {self.sensitive} \n"
        )
