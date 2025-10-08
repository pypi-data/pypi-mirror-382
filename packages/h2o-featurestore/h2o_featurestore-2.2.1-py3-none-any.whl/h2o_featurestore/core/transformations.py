import os
import shutil
import tempfile
from abc import ABC
from abc import abstractmethod
from enum import Enum

import requests

from h2o_featurestore.core.utils import StorageSession
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_generate_transformation_upload_request import (
    V1GenerateTransformationUploadRequest,
)
from h2o_featurestore.gen.model.v1_join_transformation import V1JoinTransformation
from h2o_featurestore.gen.model.v1_join_type import V1JoinType
from h2o_featurestore.gen.model.v1_mojo_transformation import V1MojoTransformation
from h2o_featurestore.gen.model.v1_spark_pipeline_transformation import (
    V1SparkPipelineTransformation,
)
from h2o_featurestore.gen.model.v1_transformation import V1Transformation
from h2o_featurestore.gen.model.v1_transformation_type import V1TransformationType

from .utils import Utils


class Transformation(ABC):
    @abstractmethod
    def _initialize(self, stub: CoreServiceApi):
        raise NotImplementedError("Method `_initialize` needs to be implemented by the child class")

    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError("Method `to_proto` needs to be implemented by the child class")

    @staticmethod
    def from_proto(proto: V1Transformation):
        if proto.get("mojo"):
            mojo = DriverlessAIMOJO(None)
            mojo.mojo_remote_location = proto.mojo.filename
            return mojo
        elif proto.get("spark_pipeline"):
            spark_pipeline = SparkPipeline(None)
            spark_pipeline.pipeline_remote_location = proto.spark_pipeline.filename
            return spark_pipeline
        elif proto.get("join"):
            return JoinFeatureSets(
                proto.join.left_key, proto.join.right_key, JoinFeatureSetsType._from_proto(proto.join.join_type)
            )


class DriverlessAIMOJO(Transformation):
    def __init__(self, mojo_local_location):
        self.mojo_local_location = mojo_local_location
        self.mojo_remote_location = None

    def _initialize(self, stub: CoreServiceApi):
        if self.mojo_remote_location is None:
            if not os.path.exists(self.mojo_local_location):
                raise Exception(f"Provided file ${self.mojo_local_location} doesn't exists.")

            md5_checksum = Utils.generate_md5_checksum(self.mojo_local_location)
            upload_response = stub.core_service_generate_transformation_upload(
                V1GenerateTransformationUploadRequest(
                    transformation_type=V1TransformationType("TransformationMojo"),
                    md5_checksum=md5_checksum,
                )
            )
            with open(self.mojo_local_location, "rb") as mojo_file:
                session = StorageSession.get_session()
                response = session.put(
                    url=upload_response.url,
                    data=mojo_file,
                    headers=upload_response.headers,
                )
                if response.status_code not in range(200, 300):
                    raise Exception(
                        f"DriverlessAIMOJO file upload failed with status code {response.status_code} "
                        f"and message {response.text}"
                    )
                self.mojo_remote_location = upload_response.filename

    def _to_proto(self):
        return V1Transformation(mojo=V1MojoTransformation(filename=self.mojo_remote_location))


class SparkPipeline(Transformation):
    def __init__(self, pipeline):
        if pipeline:
            if isinstance(pipeline, str) and pipeline.endswith(".zip"):
                if not os.path.exists(pipeline):
                    raise Exception(f"Provided file {pipeline} doesn't exists.")
                self.pipeline_local_location = pipeline
            elif isinstance(pipeline, str):
                shutil.make_archive("pipeline", "zip", pipeline)
                self.pipeline_local_location = "pipeline.zip"
            else:
                if Utils.is_running_on_databricks():
                    import random
                    import string

                    output_dir = "/tmp/" + "".join(random.choice(string.ascii_lowercase) for x in range(10))
                    remote_output_dir = "/dbfs" + output_dir
                else:
                    output_dir = tempfile.mkdtemp()
                    remote_output_dir = output_dir
                pipeline.write().overwrite().save(output_dir)
                shutil.make_archive("pipeline", "zip", remote_output_dir)
                shutil.rmtree(remote_output_dir)
                self.pipeline_local_location = "pipeline.zip"
        else:
            self.pipeline_local_location = pipeline
        self.pipeline_remote_location = None

    def _initialize(self, stub: CoreServiceApi):
        if self.pipeline_remote_location is None:
            md5_checksum = Utils.generate_md5_checksum(self.pipeline_local_location)
            upload_response = stub.core_service_generate_transformation_upload(
                V1GenerateTransformationUploadRequest(
                    transformation_type=V1TransformationType("TransformationSparkPipeline"),
                    md5_checksum=md5_checksum,
                )
            )

            with open(self.pipeline_local_location, "rb") as spark_pipeline_file:
                session = StorageSession.get_session()
                response = session.put(
                    url=upload_response.url,
                    data=spark_pipeline_file,
                    headers=upload_response.headers,
                )
                if response.status_code not in range(200, 300):
                    raise Exception(
                        f"SparkPipeline file upload failed with status code {response.status_code} "
                        f"and message {response.text}"
                    )
                self.pipeline_remote_location = upload_response.filename

    def _to_proto(self):
        return V1Transformation(spark_pipeline=V1SparkPipelineTransformation(filename=self.pipeline_remote_location))


class JoinFeatureSetsType(Enum):
    INNER = "JOIN_TYPE_INNER"
    LEFT = "JOIN_TYPE_LEFT"
    RIGHT = "JOIN_TYPE_RIGHT"
    FULL = "JOIN_TYPE_FULL"
    CROSS = "JOIN_TYPE_CROSS"

    @classmethod
    def _from_proto(cls, proto_join_type: V1JoinType):
        return cls(str(proto_join_type))

    @classmethod
    def _to_proto(cls, join_type) -> V1JoinType:
        return V1JoinType(str(join_type.value))

class JoinFeatureSets(Transformation):
    def __init__(self, left_key: str, right_key: str, join_type: JoinFeatureSetsType = JoinFeatureSetsType.INNER):
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type

    def _initialize(self, stub: CoreServiceApi):
        pass

    def _to_proto(self):
        return V1Transformation(
            join=V1JoinTransformation(
                left_key=self.left_key,
                right_key=self.right_key,
                join_type=JoinFeatureSetsType._to_proto(self.join_type),
            )
        )
