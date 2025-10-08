import datetime
from typing import Optional

from h2o_featurestore.gen.model.v1_backfill_options import V1BackfillOptions
from h2o_featurestore.gen.model.v1_spark_pipeline_transformation import (
    V1SparkPipelineTransformation,
)

from ..transformations import SparkPipeline
from ..utils import Utils


class BackfillOption:
    def __init__(
        self,
        from_version: str,
        from_date: Optional[datetime.datetime] = None,
        to_date: Optional[datetime.datetime] = None,
        spark_pipeline: Optional[SparkPipeline] = None,
        feature_mapping: Optional[dict] = None,
    ):
        self._from_version = from_version
        self._from_date = from_date
        self._to_date = to_date
        self._spark_pipeline = spark_pipeline
        self._feature_mapping = feature_mapping

    def _to_proto(self, stub):
        backfill_options = V1BackfillOptions(from_version=self._from_version)
        if self._spark_pipeline:
            self._spark_pipeline._initialize(stub)
            backfill_options.spark_pipeline = V1SparkPipelineTransformation(filename=self._spark_pipeline.pipeline_remote_location)
        if self._from_date:
            backfill_options.from_date = Utils.ensure_timezone_aware(self._from_date)
        if self._to_date:
            backfill_options.to_date = Utils.ensure_timezone_aware(self._to_date)
        if self._feature_mapping:
            backfill_options.feature_mapping = self._feature_mapping
        return backfill_options
