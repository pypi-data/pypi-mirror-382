import json

from .base_job import BaseJob


class RetrieveJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.core_service_get_retrieve_as_links_job_output(job_id=job_id.job_id)
        return response.download_links

    def __repr__(self):
        return json.dumps(
            {
                "job_id": self._job.job_id,
                "job_type": str(self._job.job_type),
                "job_done": bool(self._job.done),
                "child_job_ids": list(map(str, self._job.child_job_ids)),
            }
        )
