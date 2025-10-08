import os

import requests

from h2o_featurestore.core.utils import StorageSession
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.core_service_update_upload_status_body import (
    CoreServiceUpdateUploadStatusBody,
)
from h2o_featurestore.gen.model.v1_artifact_upload_status import V1ArtifactUploadStatus
from h2o_featurestore.gen.model.v1_store_file_artifact_request import (
    V1StoreFileArtifactRequest,
)
from h2o_featurestore.gen.model.v1_store_link_request import V1StoreLinkRequest

from .. import interactive_console
from ..entities.artifact import ArtifactFactory
from ..entities.artifact import FileArtifact
from ..entities.artifact import LinkArtifact
from ..utils import Utils


class Artifacts:
    def __init__(self, feature_set, stub: CoreServiceApi):
        self._feature_set = feature_set
        self._stub = stub
        self._feature_set_major_version = int(feature_set.version.split(".")[0])

    def store_file(self, file_path, title=None, description=None):
        store_response = self._request_backend_storage(file_path, title, description)
        interactive_console.log("Uploading file content")
        self._upload_content(file_path, store_response)
        retrieve_response = self._retrieve_artifact(store_response)
        interactive_console.log(f"File: {file_path} was successfully uploaded")
        return FileArtifact(retrieve_response.artifact, self._stub)

    def _request_backend_storage(self, file_path, title, description):
        file_name = os.path.basename(file_path)
        checksum = Utils.generate_md5_checksum(file_path)
        request = V1StoreFileArtifactRequest(
            title=title or f"File {file_name}",
            description=description or "user uploaded file",
            filename=file_name,
            feature_set_id=self._feature_set.id,
            feature_set_major_version=self._feature_set_major_version,
            md5_checksum=checksum,
        )
        store_response = self._stub.core_service_store_file_artifact(request)
        return store_response

    def _upload_content(self, file_path, store_response):
        self._update_status(store_response.artifact_id, V1ArtifactUploadStatus(
            "ARTIFACT_UPLOAD_STATUS_IN_PROGRESS"
        ))
        with open(file_path, "rb") as file:
            session = StorageSession.get_session()
            data_response = session.put(
                url=store_response.url,
                data=file,
                headers=store_response.headers,
            )
            if data_response.status_code not in range(200, 300):
                self._update_status(store_response.artifact_id, V1ArtifactUploadStatus(
                    "ARTIFACT_UPLOAD_STATUS_IN_PROGRESS"
                ))
                raise Exception(
                    f"File upload failed with status code {data_response.status_code} "
                    f"and message {data_response.text}"
                )
        self._update_status(store_response.artifact_id, V1ArtifactUploadStatus(
                    "ARTIFACT_UPLOAD_STATUS_DONE"
                ))

    def _retrieve_artifact(self, store_response):
        retrieve_response = self._stub.core_service_retrieve_artifact(artifact_id=store_response.artifact_id)
        return retrieve_response

    def _update_status(self, artifact_id, status: V1ArtifactUploadStatus):
        self._stub.core_service_update_upload_status(artifact_id=artifact_id, body=CoreServiceUpdateUploadStatusBody(
            upload_status=status
        ))

    def store_link(self, url, title=None, description=None):
        upload_response = self._upload_link(url, title, description)
        retrieve_response = self._retrieve_artifact(upload_response)
        interactive_console.log(f"Link: {url} was successfully uploaded")
        return LinkArtifact(retrieve_response.artifact, self._stub)

    def _upload_link(self, url, title, description):
        request = V1StoreLinkRequest(
            title=title or f"Link {url}",
            description=description or "user uploaded link",
            url=url,
            feature_set_id=self._feature_set.id,
            feature_set_major_version=self._feature_set_major_version,
        )
        response = self._stub.core_service_store_link(request)
        return response

    def list(self):
        """Return a generator which obtains artifacts associated with the feature set, lazily.

        Returns:
            Iterable[Artifact]: A generator iterator object consists of artifacts.

        Typical example:
            feature_set.artifacts.list()
        """
        has_next_page = True
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_artifacts(feature_set_id=self._feature_set.id, feature_set_major_version=self._feature_set_major_version, page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for artifact in response.artifacts:
                yield ArtifactFactory.create_artifact(artifact, self._stub)

    def __repr__(self):
        return "This class wraps together methods working with feature set artifacts"
