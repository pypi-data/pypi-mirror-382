from typing import List

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_feature_schema import V1FeatureSchema
from h2o_featurestore.gen.model.v1_feature_set_schema_compatibility_request import (
    V1FeatureSetSchemaCompatibilityRequest,
)
from h2o_featurestore.gen.model.v1_feature_set_schema_patch_request import (
    V1FeatureSetSchemaPatchRequest,
)

from ..schema import FeatureSchema
from ..schema import FeatureSchemaMonitoring
from ..schema import FeatureSchemaSpecialData
from ..schema import Schema


class FeatureSetSchema:
    def __init__(self, stub: CoreServiceApi, feature_set):
        self._feature_set = feature_set
        self._stub = stub

    def get(self):
        """Get a schema of a feature set.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            fs.schema.get()
        """
        return Schema.create_from(self._feature_set)

    def is_compatible_with(self, new_schema, compare_data_types=True):
        """Compare a schema of a feature set with a schema of new data source.

        Args:
            new_schema: (Schema) A new schema to check compatibility with.
            compare_data_types: (bool) Object indicates whether data type needs to be compared or not.

        Returns:
            bool: A boolean describes whether compatible or not.

        Typical example:
            fs.schema.is_compatible_with(new_schema, compare_data_types=True)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#checking-schema-compatibility
        """
        request = V1FeatureSetSchemaCompatibilityRequest()
        request.original_schema = self.get()._to_proto_schema()
        request.new_schema = new_schema._to_proto_schema()
        request.compare_data_types = compare_data_types
        response = self._stub.core_service_is_feature_set_schema_compatible(body=request)
        return response.is_compatible

    def patch_from(self, new_schema, compare_data_types=True):
        """Patch a new schema with a schema of a feature set.

        Patch schema checks for matching features between the ‘new schema’ and the existing ‘fs.schema’.
        If there is a match, then the metadata such as special_data, description, etc are copied into the new_schema.

        Args:
            new_schema: (Schema) A new schema that needs to be patched.
            compare_data_types: (bool) Object indicates whether data type are to be compared while patching.

        Returns:
            Schema: A new schema after patches.

        Typical example:
            fs.schema.patch_from(new_schema, compare_data_types=True)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#patching-new-schema
        """
        request = V1FeatureSetSchemaPatchRequest()
        request.original_schema = self.get()._to_proto_schema()
        request.new_schema = new_schema._to_proto_schema()
        request.compare_data_types = compare_data_types
        response = self._stub.core_service_feature_set_schema_patch(body=request)
        return Schema(self._create_schema_from_proto(response.schema), True)

    @staticmethod
    def _create_schema_from_proto(schema: List[V1FeatureSchema]) -> List[FeatureSchema]:
        if schema:
            return [
                FeatureSchema(
                    feature_schema.name,
                    feature_schema.data_type,
                    nested_features_schema=FeatureSetSchema._create_schema_from_proto(feature_schema.nested),
                    special_data=FeatureSchemaSpecialData(
                        spi=feature_schema.get("special_data").get("spi") if feature_schema.get("special_data") else False,
                        pci=feature_schema.get("special_data").get("pci") if feature_schema.get("special_data") else False,
                        rpi=feature_schema.get("special_data").get("rpi") if feature_schema.get("special_data") else False,
                        demographic=feature_schema.get("special_data").get("demographic") if feature_schema.get("special_data") else False,
                        sensitive=feature_schema.get("special_data").get("sensitive") if feature_schema.get("special_data") else False,
                    ),
                    _feature_type=feature_schema.feature_type.value,
                    description=feature_schema.description,
                    classifiers=set(feature_schema.classifiers) if feature_schema.classifiers else set(),
                    custom_data=feature_schema.custom_data,
                    monitoring=FeatureSchemaMonitoring(anomaly_detection=feature_schema.monitoring.anomaly_detection) if feature_schema.monitoring else None,
                )
                for feature_schema in schema
            ]
        return []