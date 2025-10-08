import logging

from ..utils import Utils
from .base_job import BaseJob


class IngestJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.core_service_get_ingest_job_output(job_id.job_id)
        result = IngestResponse(response)

        if result._get_meta_message():
            logging.info(result._get_meta_message())

        return result


class IngestResponse:
    def __init__(self, response):
        self._response = response
        self._meta = response.meta

    def _get_feature_set_id(self):
        return self._response.feature_set_id

    def _get_feature_set_version(self):
        return self._response.feature_set_version

    def _get_meta_message(self):
        return self._meta.message

    def __repr__(self):
        return Utils.pretty_print_proto(self._meta)
