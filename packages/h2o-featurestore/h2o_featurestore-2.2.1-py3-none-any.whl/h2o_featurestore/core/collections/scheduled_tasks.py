import time

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_lazy_ingest_request import V1LazyIngestRequest
from h2o_featurestore.gen.model.v1_schedule_task_request import V1ScheduleTaskRequest

from ..entities.scheduled_task import ScheduledTask
from ..job_info import JobInfo


class ScheduledTasks:
    def __init__(self, stub: CoreServiceApi, feature_set):
        self._stub = stub
        self._feature_set = feature_set

    def create_ingest_task(self, request: V1ScheduleTaskRequest):
        response = self._stub.core_service_schedule_ingest_job(request)
        return ScheduledTask(self._stub, response.task)

    def create_lazy_ingest_task(self, request: V1ScheduleTaskRequest):
        response = self._stub.core_service_schedule_lazy_ingest_task(request)
        return ScheduledTask(self._stub, response.task)

    def tasks(self):
        """List scheduled tasks.

        Returns:
            Generator of scheduled tasks

        Typical example:
            fs.schedule.tasks()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_schedule.html#to-list-scheduled-tasks
        """
        has_next_page = True
        page_size = 100
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_scheduled_tasks(
                feature_set_id=self._feature_set.id,
                page_size=page_size,
                page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for task in response.tasks:
                yield ScheduledTask(self._stub, task)

    def get(self, task_id: str):
        """Obtain a scheduled task.

        Args:
            task_id: (str) A unique id of a scheduled task.

        Returns:
            ScheduledTask: An existing scheduled task.

        Typical example:
            task = fs.schedule.get("task_id")
        """
        response = self._stub.core_service_get_scheduled_task(scheduled_task_id=task_id)
        return ScheduledTask(self._stub, response.task)

    def get_lazy_ingest_task(self):
        """Obtain a lazy ingest task.

        This retrieves an existing ingest task which is planned for later ingestion.
        Each major version of a feature set can only contain one lazy ingest task.

        Returns:
            ScheduledTask: A scheduled task.

        Typical example:
            task = fs.schedule.get_lazy_ingest_task()
        """
        response = self._stub.core_service_get_lazy_ingest_task(feature_set_id=self._feature_set.id,
                                                                feature_set_version=self._feature_set.version)
        return ScheduledTask(self._stub, response.task)

    def start_lazy_ingest_task(self):
        """Starts a lazy ingest task."""
        request = V1LazyIngestRequest(
            feature_set_id=self._feature_set.id, feature_set_version=self._feature_set.version
        )
        response = self._stub.core_service_start_lazy_ingest_task(request)
        if response.job_id:
            info = JobInfo(self._stub, response.job_id)
            while not self._get_job(response.job_id).done:
                info.show_progress()
                time.sleep(2)
            info.show_progress()  # there is possibility that some progress was pushed before finishing job

    def _get_job(self, job_id):
        return self._stub.core_service_get_job(job_id)
