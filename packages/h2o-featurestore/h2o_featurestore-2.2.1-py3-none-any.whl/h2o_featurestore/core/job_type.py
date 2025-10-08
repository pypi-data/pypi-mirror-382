from enum import Enum

from h2o_featurestore.gen.model.v1_job_type import V1JobType


class JobType(Enum):
    UNKNOWN = "Unknown"
    INGEST = "Ingest"
    RETRIEVE = "Retrieve"
    EXTRACT_SCHEMA = "ExtractSchema"
    REVERT_INGEST = "RevertIngest"
    MATERIALIZATION_ONLINE = "MaterializationOnline"
    COMPUTE_STATISTICS = "ComputeStatistics"
    COMPUTE_RECOMMENDATION_CLASSIFIERS = "ComputeRecommendationClassifiers"
    BACKFILL = "Backfill"
    OPTIMIZE_STORAGE = "OptimizeStorage"

    @classmethod
    def from_proto(cls, proto_job_type: V1JobType):
        return cls(str(proto_job_type))

    @classmethod
    def to_proto(cls, job_type) -> V1JobType:
        return V1JobType(str(job_type.value))