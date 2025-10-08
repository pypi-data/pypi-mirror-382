from .base_job import BaseJob


class ComputeRecommendationClassifiersJob(BaseJob):
    def _response_method(self, job_id):
        self._stub.core_service_get_compute_recommendation_classifiers_job_output(job_id.job_id)
