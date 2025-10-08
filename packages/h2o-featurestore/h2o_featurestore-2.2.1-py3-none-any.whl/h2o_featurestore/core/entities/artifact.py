import os
from enum import Enum

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_artifact import V1Artifact
from h2o_featurestore.gen.model.v1_artifact_type import V1ArtifactType
from h2o_featurestore.gen.model.v1_artifact_upload_status import V1ArtifactUploadStatus

from .. import interactive_console
from ..utils import Utils


class Artifact:
    def __init__(self, artifact, stub: CoreServiceApi):
        self._artifact = artifact
        self._stub = stub

    @property
    def id(self):
        return self._artifact.artifact_id

    @property
    def title(self):
        return self._artifact.title

    @property
    def description(self):
        return self._artifact.description

    @property
    def artifact_type(self):
        return ArtifactType.from_proto(self._artifact.artifact_type)

    def delete(self):
        self._stub.core_service_delete_artifact(artifact_id=self._artifact.artifact_id)
        interactive_console.log(f"Artifact '{self._artifact.title}' was deleted")

    def __repr__(self):
        return Utils.pretty_print_proto(self._artifact)


class FileArtifact(Artifact):
    def __init__(self, artifact, stub: CoreServiceApi):
        super(FileArtifact, self).__init__(artifact, stub)

    @property
    def filename(self):
        return self._artifact.filename

    @property
    def upload_status(self):
        return ArtifactUploadStatus.from_proto(self._artifact.upload_status)

    def retrieve(self, filepath, overwrite_existing_file="n"):
        if not Utils.filepath_directory_exists(filepath):
            raise Exception(f"Can't save artifact as path does not exist: '{filepath}'")

        interactive_console.log("Requesting download link")
        response = self._stub.core_service_retrieve_artifact(artifact_id=self._artifact.artifact_id)

        destination = os.path.join(filepath, response.artifact.filename) if os.path.isdir(filepath) else filepath
        if os.path.exists(destination) and overwrite_existing_file.lower() != "y":
            raise Exception(f"Artifact already exists '{destination}'")

        interactive_console.log("Downloading content")
        Utils.download_file(destination, response.artifact.url)
        interactive_console.log(f"Artifact '{self._artifact.title}' was saved into '{destination}'")


class LinkArtifact(Artifact):
    def __init__(self, artifact, stub):
        super(LinkArtifact, self).__init__(artifact, stub)

    @property
    def url(self):
        return self._artifact.url


class ArtifactFactory:
    @staticmethod
    def create_artifact(artifact: V1Artifact, stub):
        artifact_type = ArtifactType.from_proto(artifact.artifact_type)
        if artifact_type == ArtifactType.ARTIFACT_TYPE_FILE:
            return FileArtifact(artifact, stub)
        elif artifact_type == ArtifactType.ARTIFACT_TYPE_LINK:
            return LinkArtifact(artifact, stub)
        else:
            raise Exception("Unknown artifact type encountered!")


class ArtifactType(Enum):
    ARTIFACT_TYPE_UNSPECIFIED = "ARTIFACT_TYPE_UNSPECIFIED"
    ARTIFACT_TYPE_LINK = "ARTIFACT_TYPE_LINK"
    ARTIFACT_TYPE_FILE = "ARTIFACT_TYPE_FILE"

    @classmethod
    def from_proto(cls, proto_artifacts_type: V1ArtifactType):
        return cls(str(proto_artifacts_type))

class ArtifactUploadStatus(Enum):
    ARTIFACT_UPLOAD_STATUS_NOT_APPLICABLE = "ARTIFACT_UPLOAD_STATUS_NOT_APPLICABLE"
    ARTIFACT_UPLOAD_STATUS_IN_PROGRESS = "ARTIFACT_UPLOAD_STATUS_IN_PROGRESS"
    ARTIFACT_UPLOAD_STATUS_DONE = "ARTIFACT_UPLOAD_STATUS_DONE"
    ARTIFACT_UPLOAD_STATUS_FAILED = "ARTIFACT_UPLOAD_STATUS_FAILED"

    @classmethod
    def from_proto(cls, proto_upload_status: V1ArtifactUploadStatus):
        return cls(str(proto_upload_status))
