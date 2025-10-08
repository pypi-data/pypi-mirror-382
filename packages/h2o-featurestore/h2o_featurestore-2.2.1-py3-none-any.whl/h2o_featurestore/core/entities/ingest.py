from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_derived_information import V1DerivedInformation
from h2o_featurestore.gen.model.v1_start_revert_ingest_job_request import (
    V1StartRevertIngestJobRequest,
)

from .. import interactive_console
from ..data_source_wrappers import get_source
from ..retrieve_holder import RetrieveHolder
from ..utils import Utils
from .revert_ingest_job import RevertIngestJob
from .user import User


class Ingest:
    def __init__(self, stub: CoreServiceApi, feature_set, ingest):
        self._stub = stub
        self._feature_set = feature_set
        self._ingest = ingest

    def retrieve(self):
        """Retrieve data.

        Returns:
            RetrieveHolder: Returns a link as output for reference.

        Typical example:
            fs.retrieve()
        """
        return RetrieveHolder(self._stub, self._feature_set, "", "", self._ingest.ingest_id)

    @interactive_console.record_stats
    def revert(self):
        """Revert to a specific ingest.

        Reverting creates a new minor version with the data corresponding to the specific ingest removed.

        Typical example:
            ingest.revert()

        For more details:
            https://docs.h2o.ai/featurestore/api/ingest_history_api.html#reverting-ingestion
        """
        job = self.revert_async()
        return job.wait_for_result()

    def revert_async(self) -> RevertIngestJob:
        """Create a revert ingestion job for feature set.

        Returns:
            RevertIngestJob: A job for reverting ingestion.

            A job is created with a unique id and type Revert. For example:

            Job(id=<job_id>, type=Revert, done=False, childJobIds=[])

        Typical example:
            ingest.revert_async()

        Raises:
            Exception: Manual revert is not allowed on derived feature set.
        """
        if self._feature_set.get("derived_from", V1DerivedInformation()).get("transformation"):
            raise Exception("Manual revert is not allowed on derived feature set")

        request = V1StartRevertIngestJobRequest()
        request.feature_set_id = self._feature_set.id
        request.feature_set_version = self._feature_set.version
        request.ingest_id = self._ingest.ingest_id
        job_id = self._stub.core_service_start_revert_ingest_job(request)
        return RevertIngestJob(self._stub, job_id)

    @property
    def ingested_records_count(self):
        return int(self._ingest.ingested_records_count)

    @property
    def ingested_at(self):
        return Utils.timestamp_to_string(self._ingest.ingest_timestamp)

    @property
    def source(self):
        return get_source(self._ingest.source)

    @property
    def scope(self):
        return Scope(self._ingest.scope)

    @property
    def started_by(self):
        return User(self._ingest.started_by)

    def __repr__(self):
        return Utils.pretty_print_proto(self._ingest)


class Scope:
    def __init__(self, scope):
        self._scope = scope

    @property
    def start_date_time(self):
        return Utils.timestamp_to_string(self._scope.start_date_time)

    @property
    def end_date_time(self):
        return Utils.timestamp_to_string(self._scope.end_date_time)

    def __repr__(self):
        return Utils.pretty_print_proto(self._scope)

    def __str__(self):
        return (
            f"Start date & time : {self._scope.start_date_time} \n"
            f"End date & time   : {self._scope.end_date_time} \n"
        )
