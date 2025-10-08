from ..utils import Utils
from .base_job import BaseJob


class OptimizeStorageJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.core_service_get_optimize_storage_job_output(job_id.job_id)
        return OptimizeStorageResponse(response)


class OptimizeStorageResponse:
    def __init__(self, response):
        self._response = response
        self._optimization_metrics = response.optimization_metrics

    @property
    def optimization_metrics(self):
        return self._optimization_metrics

    def __repr__(self):
        return Utils.pretty_print_proto(self._response)
