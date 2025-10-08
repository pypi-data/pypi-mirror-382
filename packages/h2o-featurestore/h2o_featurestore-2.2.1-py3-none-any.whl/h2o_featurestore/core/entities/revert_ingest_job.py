from .base_job import BaseJob


class RevertIngestJob(BaseJob):
    def _response_method(self, job_id):
        self._stub.core_service_get_revert_ingest_job_output(job_id=job_id.job_id)
