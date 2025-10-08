from ..schema import FeatureSchema
from ..schema import Schema
from ..schema import SchemaDerivation
from ..schema import VersionedId
from ..transformations import Transformation
from .base_job import BaseJob


class ExtractSchemaJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.core_service_get_extract_schema_job_output(job_id.job_id)
        derivation = None
        if response.derived_from and response.derived_from.transformation:
            derivation = SchemaDerivation(
                [VersionedId(f.id, f.major_version) for f in response.derived_from.feature_set_ids],
                Transformation.from_proto(response.derived_from.transformation),
            )
        return Schema(
            ExtractSchemaJob._features_schema_from_proto(response.schema),
            True,
            derivation,
        )

    @staticmethod
    def _features_schema_from_proto(schema):
        return [
            FeatureSchema(
                feature_schema.name,
                feature_schema.data_type,
                nested_features_schema=ExtractSchemaJob._features_schema_from_proto(feature_schema.nested),
            )
            for feature_schema in schema
        ]
