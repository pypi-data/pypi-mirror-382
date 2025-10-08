from ..utils import Utils


class TaskExecutionHistory:
    """Wrapper around internal execution history record.

    Typical example:
        for execution_record in scheduled_task.execution_history:
          print(execution_record)
    """

    def __init__(self, execution_record):
        self._execution_record = execution_record

    @property
    def job_id(self):
        return self._execution_record.job_id.job_id

    @property
    def started_at(self):
        return Utils.timestamp_to_string(self._execution_record.started_at)

    @property
    def finished_at(self):
        return Utils.timestamp_to_string(self._execution_record.finished_at)

    @property
    def final_status(self):
        return str(self._execution_record.final_status)

    def __repr__(self):
        return Utils.pretty_print_proto(self._execution_record)

    def __str__(self):
        return (
            f"Job Id        : {self.job_id}\n"
            f"Started at    : {self.started_at}\n"
            f"Finished at   : {self.finished_at}\n"
            f"Final status  : {self.final_status}\n"
        )
