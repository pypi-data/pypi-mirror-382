import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from h2o_featurestore.core.entities import feature_set
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_job_id import V1JobId
from h2o_featurestore.gen.model.v1_lazy_ingest_request import V1LazyIngestRequest
from h2o_featurestore.gen.model.v1_retrieve_as_spark_response import (
    V1RetrieveAsSparkResponse,
)
from h2o_featurestore.gen.model.v1_retrieve_request import V1RetrieveRequest

from .commons.spark_utils import SparkUtils
from .job_info import JobInfo
from .utils import Utils


class RetrieveAsLinksCommon:
    def __init__(self, stub: CoreServiceApi, feature_set, start_date_time: str, end_date_time: str, ingest_id: str):
        self._stub = stub
        self._thread_pool = ThreadPoolExecutor(5)
        self._feature_set = feature_set
        self._start_date_time = start_date_time
        self._end_date_time = end_date_time
        self._ingest_id = ingest_id
        self._job_id: Optional[V1JobId] = None

    def _get_job(self, job_id):
        return self._stub.core_service_get_job(job_id=job_id.job_id)

    def _get_retrieve_links_output(self, job_id):
        return self._stub.core_service_get_retrieve_as_links_job_output(job_id=job_id.job_id)

    def download(self, output_dir=None):
        """Downloads files to the specified directory location.

        Args:
            output_dir: (str) A directory location as string. Default is None.

        Returns:
            str: A directory path where the files are downloaded.

        Typical usage example:

            retrieve_job = client.jobs.get(<job id>)
            dir = retrieve_job.download()

        For more details:
            https://docs.h2o.ai/featurestore/api/jobs_api.html#how-to-download-using-retrievejob
        """
        self._process_lazy_ingest_task()
        if not self._job_id:
            self._job_id = self._start_retrieve_links_job()

        info = JobInfo(self._stub, self._job_id)
        while not self._get_job(self._job_id).done:
            info.show_progress()
            time.sleep(2)
        info.show_progress()  # there is possibility that some progress was pushed before finishing job
        retrieve_as_links_response = self._get_retrieve_links_output(self._job_id)
        return Utils.download_files(output_dir, retrieve_as_links_response.download_links)

    def download_async(self, output_dir=None):
        """Downloads files asynchronously to the specified directory location.

        Args:
            output_dir: (str) A directory location as string. Default is None.

        Returns:
            DownloadFuture: Represents a job.

            It contains is_done and get_status methods. For example:

            future.is_done() -> check whether job has finished or not
            future.get_status() -> > return job's status

        Typical usage example:

            retrieve_job = client.jobs.get(<job id>)
            future = retrieve_job.download_async()

        For more details:
            https://docs.h2o.ai/featurestore/api/jobs_api.html#how-to-download-using-retrievejob
        """
        future = self._thread_pool.submit(self.download, output_dir)
        return DownloadFuture(future)

    def _start_retrieve_links_job(self):
        request = self._create_retrieve_request()
        return self._stub.core_service_start_retrieve_as_links_job(body=request)

    def _create_retrieve_request(self, spark_session=None):
        session_id = ""
        if spark_session is not None:
            session_id = spark_session.conf.get("ai.h2o.featurestore.sessionId", "")
        request = V1RetrieveRequest()
        request.feature_set_id = self._feature_set.id
        request.feature_set_version = self._feature_set.version
        request.session_id = session_id
        if self._start_date_time is not None:
            request.start_date_time = self._start_date_time
        if self._end_date_time is not None:
            request.end_date_time = self._end_date_time
        request.ingest_id = self._ingest_id
        return request

    def _process_lazy_ingest_task(self):
        request = V1LazyIngestRequest(
            feature_set_id=self._feature_set.id, feature_set_version=self._feature_set.version
        )
        response = self._stub.core_service_start_lazy_ingest_task(request)
        if response.job_id and response.job_id.job_id:
            logging.info(
                "No previous ingestion found. Lazy ingest task will start. "
                "New minor version will be created and retrieved from."
            )
            info = JobInfo(self._stub, response.job_id)
            while not self._get_job(response.job_id).done:
                info.show_progress()
                time.sleep(2)
            info.show_progress()  # there is possibility that some progress was pushed before finishing job
            feature_set_response = self._stub.core_service_get_ingest_job_output(response.job_id.job_id).feature_set
            self._feature_set.version = feature_set_response.version


class RetrieveHolder(RetrieveAsLinksCommon):
    def __init__(self, stub: CoreServiceApi, feature_set, start_date_time: str, end_date_time: str, ingest_id: str):
        super().__init__(stub, feature_set, start_date_time, end_date_time, ingest_id)
        self._stub = stub
        self._retrieve_as_spark_response: Optional[V1RetrieveAsSparkResponse] = None

    def download(self, output_dir=None):
        """Downloads files to the specified directory location.

        Args:
            output_dir: (str) A directory location as string. Default is None.

        Returns:
            str: A directory path where the files are downloaded.

        Typical usage example:

            ref = feature_set.retrieve()
            dir = ref.download()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#downloading-the-files-from-feature-store
        """
        return super(RetrieveHolder, self).download(output_dir)

    def download_async(self, output_dir=None):
        """Downloads files asynchronously to the specified directory location.

        Args:
            output_dir: (str) A directory location as string. Default is None.

        Returns:
            DownloadFuture: Represents a job.

            It contains is_done and get_status methods. For example:

            future.is_done() -> check whether job has finished or not
            future.get_status() -> return job's status

        Typical usage example:

            ref = feature_set.retrieve()
            future = ref.download_async()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#downloading-the-files-from-feature-store
        """
        return super(RetrieveHolder, self).download_async(output_dir)

    def as_spark_frame(self, spark_session):
        """Returns a spark data frame.

        Generates a data frame of the retrieved data using spark session.

        Args:
            spark_session: (SparkSession) Represents a spark session.

        Returns:
            DataFrame: Represents a spark data frame.

            The frame is made up of columns as features and rows as records.
            Rows contain data within retrieve scope (filtered).

        Typical usage example:

            ref = feature_set.retrieve()
            data_frame = ref.as_spark_frame(spark_session)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#obtaining-data-as-a-spark-frame
        """
        from pyspark.sql.functions import col  # type: ignore
        from pyspark.sql.functions import from_utc_timestamp  # type: ignore
        from pyspark.sql.functions import lit  # type: ignore
        from pyspark.sql.functions import to_timestamp  # type: ignore
        from pyspark.sql.functions import unix_timestamp  # type: ignore
        from pyspark.sql.types import TimestampType  # type: ignore

        self._process_lazy_ingest_task()
        if self._retrieve_as_spark_response is None:
            request = self._create_retrieve_request(spark_session)
            self._retrieve_as_spark_response = self._stub.core_service_retrieve_as_spark(body=request)
        resp = self._retrieve_as_spark_response
        spark_session.conf.set("ai.h2o.featurestore.sessionId", resp.session_id)
        SparkUtils.configure_user_spark(spark_session)
        for k, v in resp.options.items():
            spark_session.conf.set(k, v)
        df = self.__load_data_frame_from_delta(resp, spark_session)

        retrieve_scope = resp.retrieve_scope
        start_timestamp = int(retrieve_scope.start_date_time.timestamp())
        end_timestamp = int(retrieve_scope.end_date_time.timestamp())
        timestamp_col = "timestamp_" + str(round(time.time() * 1000))
        if self._ingest_id:
            output_df = df.filter(col("ingest_id") == lit(self._ingest_id))
        elif self._feature_set.time_travel_column:
            output_df = (
                df.withColumn(
                    timestamp_col,
                    unix_timestamp(
                        from_utc_timestamp(
                            to_timestamp(
                                col(self._feature_set.time_travel_column),
                                self._feature_set.time_travel_column_format,
                            ),
                            spark_session.conf.get("spark.sql.session.timeZone"),
                        )
                    ),
                )
                .filter(col(timestamp_col) <= end_timestamp)
                .filter(col(timestamp_col) >= start_timestamp)
            ).drop(timestamp_col)
        else:
            output_df = (
                df.filter(col("time_travel_column_auto_generated") <= end_timestamp)
                .filter(col("time_travel_column_auto_generated") >= start_timestamp)
                .withColumn(
                    "time_travel_column_auto_generated",
                    col("time_travel_column_auto_generated").cast(TimestampType()),
                )
            )
        internal_columns = ["ingest_id"] + [column for column in df.columns if column.startswith("__")]
        return output_df.drop(*internal_columns)

    def __load_data_frame_from_delta(self, resp: V1RetrieveAsSparkResponse, spark_session):
        if self._retrieve_as_spark_response is None:
            raise Exception("Retrieve as spark response is not available")
        if self._retrieve_as_spark_response.delta_version == -1:
            df = spark_session.read.format("delta").load(resp.cache_path)
        else:
            df = (
                spark_session.read.format("delta")
                .option("versionAsOf", self._retrieve_as_spark_response.delta_version)
                .load(resp.cache_path)
            )
        return df
class DownloadFuture:
    def __init__(self, future):
        self._future = future
        self._result = None

    def is_done(self) -> bool:
        """Checks whether job has finished or not."""
        return self._future.done()

    def get_result(self):
        """Returns job's final result.

        Returns:
            Schema: A resultant schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

            Above result is the output of asynchronous job for schema extraction.

        Typical example:

            job = client.extract_schema_from_source_async(source)
            schema.get_result()

        Raises:
            Exception: Job has not finished yet!
        """
        if not self._result:
            if not self.is_done():
                raise Exception("Job has not finished yet!")
            self._result = self._future.result()
        return self._result
