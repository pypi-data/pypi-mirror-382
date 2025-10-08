import datetime
import json
import logging
import re
import time
from copy import deepcopy
from typing import Optional

import tzlocal

from h2o_featurestore.core.job_type import JobType
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.apis import OnlineServiceApi
from h2o_featurestore.gen.model.apiv1_feature_set import Apiv1FeatureSet
from h2o_featurestore.gen.model.core_service_add_feature_set_permission_body import (
    CoreServiceAddFeatureSetPermissionBody,
)
from h2o_featurestore.gen.model.core_service_create_new_feature_set_version_body import (
    CoreServiceCreateNewFeatureSetVersionBody,
)
from h2o_featurestore.gen.model.core_service_remove_feature_set_permission_body import (
    CoreServiceRemoveFeatureSetPermissionBody,
)
from h2o_featurestore.gen.model.core_service_submit_pending_feature_set_permission_body import (
    CoreServiceSubmitPendingFeatureSetPermissionBody,
)
from h2o_featurestore.gen.model.core_service_update_feature_set_body import (
    CoreServiceUpdateFeatureSetBody,
)
from h2o_featurestore.gen.model.online_service_online_ingestion_body import (
    OnlineServiceOnlineIngestionBody,
)
from h2o_featurestore.gen.model.v1_feature_set_type import V1FeatureSetType
from h2o_featurestore.gen.model.v1_listable_feature_set import V1ListableFeatureSet
from h2o_featurestore.gen.model.v1_offline_time_to_live_interval import (
    V1OfflineTimeToLiveInterval,
)
from h2o_featurestore.gen.model.v1_online_ingestion_token_response import (
    V1OnlineIngestionTokenResponse,
)
from h2o_featurestore.gen.model.v1_online_retrieve_token_response import (
    V1OnlineRetrieveTokenResponse,
)
from h2o_featurestore.gen.model.v1_online_time_to_live_interval import (
    V1OnlineTimeToLiveInterval,
)
from h2o_featurestore.gen.model.v1_permission_type import V1PermissionType
from h2o_featurestore.gen.model.v1_process_interval_unit import V1ProcessIntervalUnit
from h2o_featurestore.gen.model.v1_schedule_task_request import V1ScheduleTaskRequest
from h2o_featurestore.gen.model.v1_start_ingest_job_request import (
    V1StartIngestJobRequest,
)
from h2o_featurestore.gen.model.v1_start_optimize_storage_job_request import (
    V1StartOptimizeStorageJobRequest,
)
from h2o_featurestore.gen.model.v1_updatable_feature_set_field import (
    V1UpdatableFeatureSetField,
)

from .. import interactive_console
from ..access_type import AccessType
from ..browser import Browser
from ..collections.artifacts import Artifacts
from ..collections.ingest_history import IngestHistory
from ..collections.scheduled_tasks import ScheduledTasks
from ..commons.case_insensitive_dict import CaseInsensitiveDict
from ..credentials import CredentialsHelper
from ..data_source_wrappers import DataSourceWrapper
from ..entities.backfill_option import BackfillOption
from ..entities.feature import Feature
from ..feature_set_flow import FeatureSetFlow
from ..retrieve_holder import RetrieveHolder
from ..storage_optimization import StorageOptimization
from ..storage_optimization import ZOrderByOptimization
from ..utils import Utils
from .feature_set_ref import FeatureSetRef
from .feature_set_schema import FeatureSetSchema
from .ingest_job import IngestJob
from .materialization_online_job import MaterializationOnlineJob
from .optimize_storage_job import OptimizeStorageJob
from .recommendation import Recommendation
from .user import User
from .user_with_permission import UserWithPermission


class OnlineToken:
    def __init__(self, feature_set_id: str, feature_set_major_version: int, token: str, signature: str, valid_to: datetime.datetime):
        self.feature_set_id = feature_set_id
        self.feature_set_major_version = feature_set_major_version
        self.token = token
        self.signature = signature
        self.valid_to = valid_to

    def is_valid_for(self, feature_set_id, feature_set_major_version):
        return (
            self.valid_to > (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1))
            and self.feature_set_id == feature_set_id
            and self.feature_set_major_version == feature_set_major_version
        )


class FeatureSet:
    def __init__(self, stub: CoreServiceApi, online_stub: OnlineServiceApi, feature_set):
        self._feature_set = deepcopy(feature_set)
        self._stub = stub
        self._online_stub: OnlineServiceApi = online_stub
        self._online_ingestion_token: Optional[OnlineToken] = None
        self._online_retrieval_token: Optional[OnlineToken] = None

    @classmethod
    def from_listable_feature_set(cls, stub: CoreServiceApi, online_stub: OnlineServiceApi, listable_feature_set: V1ListableFeatureSet):
        fs = Apiv1FeatureSet()
        fs.project = listable_feature_set.get("project_name", "")
        fs.feature_set_name = listable_feature_set.get("name", "")
        fs.version = listable_feature_set.get("version", "")
        fs.version_change = listable_feature_set.get("version_change", "")
        fs.time_travel_column = listable_feature_set.get("time_travel_column", "")
        fs.time_travel_column_format = listable_feature_set.get("time_travel_column_format", "")
        if listable_feature_set.get("feature_set_type"):
            fs.feature_set_type = listable_feature_set.feature_set_type
        fs.description = listable_feature_set.get("description", "")
        if listable_feature_set.get("author"):
            fs.author = deepcopy(listable_feature_set.get("author"))
        if listable_feature_set.get("created_date_time"):
            fs.created_date_time = deepcopy(listable_feature_set.get("created_date_time"))
        if listable_feature_set.get("last_update_date_time"):
            fs.last_update_date_time = deepcopy(listable_feature_set.get("last_update_date_time"))
        fs.application_name = listable_feature_set.get("application_name", "")
        fs.deprecated = listable_feature_set.get("deprecated", False)
        if listable_feature_set.get("deprecated_date"):
            fs.deprecated_date = listable_feature_set.get("deprecated_date")
        fs.data_source_domains = listable_feature_set.get("data_source_domains", [])
        fs.tags = listable_feature_set.get("tags", [])
        fs.process_interval = listable_feature_set.get("process_interval", 0)
        if listable_feature_set.get("process_interval_unit"):
            fs.process_interval_unit = listable_feature_set.get("process_interval_unit")
        if listable_feature_set.get("flow"):
            fs.flow = FeatureSetFlow._from_proto(listable_feature_set.flow).name
        if listable_feature_set.get("time_to_live"):
            fs.time_to_live = deepcopy(listable_feature_set.get("time_to_live"))
        if listable_feature_set.get("statistics"):
            fs.statistics = deepcopy(listable_feature_set.statistics)
        if listable_feature_set.get("special_data"):
            fs.special_data = deepcopy(listable_feature_set.special_data)
        if listable_feature_set.get("primary_key"):
            fs.primary_key = list(listable_feature_set.primary_key)
        fs.id = listable_feature_set.get("id", "")
        if listable_feature_set.get("time_travel_scope"):
            fs.time_travel_scope = deepcopy(listable_feature_set.get("time_travel_scope", None))
        fs.application_id = listable_feature_set.get("application_id", "")
        fs.feature_set_state = listable_feature_set.get("feature_set_state", "")
        if listable_feature_set.get("online"):
            fs.online = deepcopy(listable_feature_set.get("online"))
        fs.project_id = listable_feature_set.get("project_id", "")
        if listable_feature_set.get("partition_by"):
            fs.partition_by = listable_feature_set.get("partition_by")
        fs.custom_data = deepcopy(listable_feature_set.get("custom_data", {}))
        if listable_feature_set.get("online_materialization_scope"):
            fs.online_materialization_scope = deepcopy(listable_feature_set.online_materialization_scope)
        if listable_feature_set.get("derived_from"):
            fs.derived_from = deepcopy(listable_feature_set.derived_from)
        fs.feature_classifiers = listable_feature_set.get("feature_classifiers", [])
        if listable_feature_set.get("last_updated_by"):
            fs.last_updated_by = deepcopy(listable_feature_set.get("last_updated_by"))
        return cls(stub, online_stub, fs)

    @property
    def id(self):
        return self._feature_set.id

    @property
    def project(self):
        return self._feature_set.project

    @property
    def feature_set_name(self):
        return self._feature_set.feature_set_name

    @property
    def version(self) -> str:
        return self._feature_set.version

    @property
    def major_version(self) -> int:
        return int(self.version.split(".")[0])

    @property
    def version_change(self):
        return self._feature_set.version_change

    @property
    def time_travel_column(self):
        return self._feature_set.time_travel_column

    @property
    def partition_by(self):
        return self._feature_set.partition_by

    @property
    def time_travel_column_format(self):
        return self._feature_set.time_travel_column_format

    @property
    def feature_set_type(self):
        return str(self._feature_set.feature_set_type)

    @feature_set_type.setter
    def feature_set_type(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            type=V1FeatureSetType(value),
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_TYPE")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def description(self):
        return self._feature_set.description

    @description.setter
    def description(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            description=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_DESCRIPTION")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def author(self):
        return User(self._feature_set.author)

    @property
    def created_date_time(self):
        return Utils.timestamp_to_string(self._feature_set.created_date_time)

    @property
    def last_update_date_time(self):
        return Utils.timestamp_to_string(self._feature_set.last_update_date_time)

    @property
    def last_updated_by(self):
        return User(self._feature_set.last_updated_by)

    @property
    def application_name(self):
        return self._feature_set.application_name

    @application_name.setter
    def application_name(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            application_name=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_APPLICATION_NAME")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def deprecated(self):
        return self._feature_set.deprecated

    @deprecated.setter
    def deprecated(self, value: bool):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            deprecated=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_DEPRECATED")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def deprecated_date(self):
        return Utils.timestamp_to_string(self._feature_set.deprecated_date)

    @property
    def data_source_domains(self):
        return self._feature_set.data_source_domains

    @data_source_domains.setter
    def data_source_domains(self, value):
        if not isinstance(value, list):
            raise ValueError("data_source_domains accepts only list of strings as a value")
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            data_source_domains=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_DATA_SOURCE_DOMAINS")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def tags(self):
        return self._feature_set.tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, list):
            raise ValueError("tags accepts only list of strings as a value")
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            tags=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_TAGS")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def process_interval(self):
        return self._feature_set.process_interval

    @process_interval.setter
    def process_interval(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            process_interval=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_PROCESS_INTERVAL")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def process_interval_unit(self):
        return str(self._feature_set.process_interval_unit)

    @process_interval_unit.setter
    def process_interval_unit(self, value: V1ProcessIntervalUnit):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            process_interval_unit=V1ProcessIntervalUnit(value),
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_PROCESS_INTERVAL_UNIT")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def flow(self) -> FeatureSetFlow:
        return FeatureSetFlow[self._feature_set.flow]

    @flow.setter
    def flow(self, value: FeatureSetFlow):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            flow=value.name,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_FLOW")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def features(self):
        if self._feature_set.features:
            return CaseInsensitiveDict(
                {
                    feature.name: Feature(
                        self._stub,
                        self,
                        feature,
                        feature.name,
                        f"`{feature.name}`" if "." in feature.name else feature.name,
                    )
                    for feature in self._feature_set.features
                }
            )
        else:
            return CaseInsensitiveDict(
                {
                    feature.name: Feature(
                        self._stub,
                        self,
                        feature,
                        feature.name,
                        f"`{feature.name}`" if "." in feature.name else feature.name,
                    )
                    for feature in self._stub.core_service_list_features(
                        feature_set_id=self._feature_set.id,
                        feature_set_version=self._feature_set.version,
                        page_size=10000).features
                }
            )

    @property
    def primary_key(self):
        return self._feature_set.primary_key

    @property
    def statistics(self):
        return Statistics(self._feature_set)

    @property
    def time_to_live(self):
        return TimeToLive(self._stub, self)

    @property
    def special_data(self):
        return FeatureSetSpecialData(self._stub, self)

    @property
    def time_travel_scope(self):
        return FeatureSetScope(self._feature_set)

    @property
    def application_id(self):
        return self._feature_set.application_id

    @application_id.setter
    def application_id(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            fapplication_id=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_APPLICATION_ID")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

        self._feature_set = self._stub.core_service_update_feature_set(
                    feature_set_id=self._feature_set.id,
                    body=update_request).updated_feature_set

    @property
    def feature_set_state(self):
        return self._feature_set.feature_set_state

    @feature_set_state.setter
    def feature_set_state(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            state=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_STATE")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def online(self):
        return Online(self._feature_set)

    @property
    def custom_data(self):
        return self._feature_set.custom_data

    @custom_data.setter
    def custom_data(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._feature_set.version,
            custom_data=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_CUSTOM_DATA")],
        )
        self._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def feature_classifiers(self):
        return self._feature_set.feature_classifiers

    def is_derived(self):
        """Ensure its derivation from another feature set."""
        if not self._feature_set.derived_from:
            return False
        return self._feature_set.derived_from.get("transformation")

    def _reference(self) -> FeatureSetRef:
        return FeatureSetRef(self.id, self.major_version)


    def create_new_version(
        self,
        schema=None,
        affected_features=None,
        reason="",
        primary_key=None,
        partition_by=None,
        time_travel_column_as_partition=False,
        backfill_options: Optional[BackfillOption] = None,
        time_travel_column=None,
        time_travel_column_format=None,
    ):
        """Create a new version of feature set.

        Args:
            schema: (Schema) A feature set schema.
            affected_features: (list[str]) A list of feature names.
            reason: (str) A reason for creating new version. By default, an auto-generated message will be populated
              describing the features added/removed/modified.
            primary_key: (list[str]) A feature name / list of feature names.
            partition_by: (list[str]) A feature name / list of feature names.
            time_travel_column_as_partition: (bool) Feature Store uses time travel column for data partitioning.
            backfill_options: (BackfillOption) Object represents backfill. It is optional.
            time_travel_column: (str) A feature column in a schema.
            time_travel_column_format: (str) Format for time travel column.

        Returns:
            FeatureSet: A feature set with new version.

        Typical example:
            new_fs = fs.create_new_version(schema=schema, reason="some message", primary_key=[])
            new_fs = fs.create_new_version(affected_features=["xyz"], reason="Computation of feature XYZ changed")
            new_fs = fs.create_new_version(schema=schema, reason="some message", backfill_options=backfill)

        Raises:
            ValueError: At least one of schema, affected_features or primary_key must be defined.

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_new_version.html
        """
        request = CoreServiceCreateNewFeatureSetVersionBody(
            feature_set_version = self._feature_set.version,
            reason = reason
        )
        if schema:
            request.schema = schema._to_proto_schema()
            if schema.is_derived():
                request.derived_from = schema.derivation._to_proto()
        else:
            request.schema = self.schema.get()._to_proto_schema()
        if affected_features:
            request.affected_features = list(affected_features)
        if primary_key:
            request.primary_key = list(primary_key)

        else:
            request.use_primary_key_from_previous_version = True
        if partition_by:
            request.partition_by = list(partition_by)

        else:
            request.use_partition_by_from_previous_version = True
        request.use_time_travel_column_as_partition = time_travel_column_as_partition
        if backfill_options:
            request.backfill_options = backfill_options._to_proto(self._stub)
        if time_travel_column is not None:
            request.time_travel_column = time_travel_column
        else:
            request.use_time_travel_column_from_previous_version = True
        if time_travel_column_format is not None:
            request.time_travel_column_format = time_travel_column_format
        else:
            request.use_time_travel_column_format_from_previous_version = True

        response = self._stub.core_service_create_new_feature_set_version(self._feature_set.id, request)
        if backfill_options:
            logging.info(
                f"Backfill started with job id: '{response.job.job_id}'. Please use this job id to track progress."
            )
        return FeatureSet(self._stub, self._online_stub, response.feature_set)

    def refresh(self):
        """Refresh a feature set.

        This obtains the latest information of feature set.

        Returns:
            FeatureSet: A feature set with the latest information.
        """
        self._feature_set = self._stub.core_service_get_feature_sets_last_minor_for_current_major(
            feature_set_id=self._feature_set.id, feature_set_version=self._feature_set.version
        ).feature_set
        return self

    def delete(self, wait_for_completion=False):
        """Deletes feature set."""
        self._stub.core_service_delete_feature_set(self._feature_set.id)
        if wait_for_completion:
            while self._stub.core_service_feature_set_exists(feature_set_id=self._feature_set.id).exists:
                time.sleep(1)
                logging.debug(f"Waiting for feature set '{self._feature_set.feature_set_name}' deletion...")
        logging.info(f"Feature set '{self._feature_set.feature_set_name}' is deleted")

    def add_owners(self, user_emails):
        """Add additional owner/owners to a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.add_owners(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Owner"))

    def add_editors(self, user_emails):
        """Add additional editor/editors to a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.add_editors(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Editor"))

    def add_consumers(self, user_emails):
        """Add additional consumer/consumers to a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.add_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Consumer"))

    def add_sensitive_consumers(self, user_emails):
        """Add additional sensitive consumer/consumers to a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.add_sensitive_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._add_permissions(user_emails, V1PermissionType("SensitiveConsumer"))

    def add_viewers(self, user_emails):
        """Add additional viewer/viewers to a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.add_viewers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._add_permissions(user_emails, V1PermissionType("Viewer"))

    def remove_owners(self, user_emails):
        """Removes owner/owners from a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.remove_owners(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Owner"))

    def remove_editors(self, user_emails):
        """Remove editor/editors from a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.remove_editors(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Editor"))

    def remove_consumers(self, user_emails):
        """Remove consumer/consumers from a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.remove_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Consumer"))

    def remove_sensitive_consumers(self, user_emails):
        """Remove sensitive consumer/consumers from a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.remove_sensitive_consumers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("SensitiveConsumer"))

    def remove_viewers(self, user_emails):
        """Remove viewer/viewers from a feature set.

        Args:
            user_emails: (list[str]]) A collection of user emails.

        Returns:
            FeatureSet: An existing feature set with the latest information.

        Typical example:
            fs.remove_viewers(["bob@h2o.ai", "alice@h2o.ai"])

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#feature-set-permissions-api
        """
        return self._remove_permissions(user_emails, V1PermissionType("Viewer"))

    def get_active_jobs(self, job_type=JobType.UNKNOWN):
        """List running jobs belonging to a feature set.

        This returns a list of jobs that are currently processing for a specific feature set.
        It also retrieves a specific type of job.

        Args:
            job_type: (JobType) A job type.
              INGEST | RETRIEVE | EXTRACT_SCHEMA | REVERT_INGEST | MATERIALIZATION_ONLINE | COMPUTE_STATISTICS |
              COMPUTE_RECOMMENDATION_CLASSIFIERS | BACKFILL | OPTIMIZE_STORAGE

        Returns:
            list[BaseJob]: A collection of active jobs.

            For example:

            [Job(id=test123, type=Ingest, done=False, childJobIds=[]),
            Job(id=test456, type=Backfill, done=False, childJobIds=[])]

        Typical example:
            fs.get_active_jobs()
            fs.get_active_jobs(job_type=INGEST)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#feature-set-jobs-api
        """
        return self._get_jobs(True, job_type)

    def _get_jobs(self, active, job_type: JobType=JobType.UNKNOWN):
        from ..collections.jobs import Jobs  # Lazy import to avoid circular reference

        response = self._stub.core_service_list_jobs(
            feature_set_id = self._feature_set.id,
            job_type = str(JobType.to_proto(job_type)),
            active = active,
        )
        return [Jobs._create_job(self._stub, job_proto) for job_proto in response.jobs]

    def _add_permissions(self, user_emails, permission):
        request = CoreServiceAddFeatureSetPermissionBody()
        request.user_emails = user_emails if isinstance(user_emails, list) else [user_emails]
        request.permission = permission
        self._stub.core_service_add_feature_set_permission(
            feature_set_id=self._feature_set.id,
            body=request,
        )
        return self

    def _remove_permissions(self, user_emails, permission):
        request = CoreServiceRemoveFeatureSetPermissionBody()
        request.user_emails = user_emails if isinstance(user_emails, list) else [user_emails]
        request.permission = permission
        self._stub.core_service_remove_feature_set_permission(
            feature_set_id=self._feature_set.id,
            body=request,
        )
        return self

    def request_access(self, access_type, reason):
        """Request feature set permissions.

        Args:
            access_type: (PermissionType) A permission type.
                OWNER | EDITOR | CONSUMER | SENSITIVE_CONSUMER
            reason: (str) A reason for permission request.

        Returns:
            str: A permission id.

        Typical example:
            my_request_id = fs.request_access(AccessType.CONSUMER, "Preparing the best model")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-feature-set-permissions
        """
        request = CoreServiceSubmitPendingFeatureSetPermissionBody()
        request.permission = AccessType.to_proto_permission(access_type)
        request.reason = reason
        response = self._stub.core_service_submit_pending_feature_set_permission(
            resource_id=self._feature_set.id,
            body=request,
        )
        return response.permission_id

    @property
    def current_permission(self):
        """Lists current feature set permissions."""
        response = self._stub.core_service_get_active_feature_set_permission(
            resource_id=self._feature_set.id
        )
        print(response.permission)
        return AccessType.from_proto_active_permission(response.permission)

    def ingest_async(
        self,
        source: DataSourceWrapper,
        credentials=None,
    ):
        """Create an ingestion job for a feature set.

        Args:
            source: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials)
              To access the provided data source. Default is None.

        Returns:
            IngestJob: A job for ingestion.

            A job is created with unique id and type Ingest. For example:

            Job(id=<job_id>, type=Ingest, done=False, childJobIds=[])

        Typical example:
            fs.ingest_async(source, credentials=credentials)

        Raises:
            Exception: Manual ingest is not allowed on derived feature set.
        """
        if self.is_derived():
            raise Exception("Manual ingest is not allowed on derived feature set")

        data_source = source.get_raw_data_location(self._stub)
        request = V1StartIngestJobRequest()
        request.feature_set_id = self._feature_set.id
        request.feature_set_version = self._feature_set.version
        request.data_source = data_source
        if not source.is_local():
            CredentialsHelper.set_credentials(request, data_source, credentials)
        job_id = self._stub.core_service_start_ingest_job(body=request)
        return IngestJob(self._stub, job_id)

    @interactive_console.record_stats
    def ingest(
        self,
        source,
        credentials=None,
    ):
        """Ingest data into the Feature Store (Offline ingestion).

        Args:
            source: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials)
              To access the provided data source. Default is None.

        Typical example:
            fs.ingest(source, credentials=credentials)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#offline-ingestion
        """
        job = self.ingest_async(source, credentials)
        result = job.wait_for_result()
        self._feature_set = self._stub.core_service_get_feature_set_by_id(
            feature_set_id=result._get_feature_set_id(),
            feature_set_version=result._get_feature_set_version(),
        ).feature_set

        return result

    def materialize_online_async(self):
        """Create a job for feature set online materialization.

        Returns:
            MaterializationOnlineJob: A job for online materialization.

            A job is created with a unique id and type MaterializationOnline. For example:

            Job(id=<job_id>, type=MaterializationOnline, done=False, childJobIds=[])

        Typical example:
            future = feature_set.materialize_online_async()
        """
        job_id = self._stub.core_service_start_materialization_online_job(
            feature_set_id=self._feature_set.id,
            feature_set_version=self._feature_set.version
        )
        return MaterializationOnlineJob(self._stub, job_id)

    @interactive_console.record_stats
    def materialize_online(self):
        """Materialize a feature set in the offline store to online.

        This pushes existing data from offline Feature store into online.

        Typical example:
            feature_set.materialize_online()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#offline-to-online-api
        """
        job = self.materialize_online_async()
        return job.wait_for_result()

    def ingest_online(self, rows):
        """Ingest data into the online Feature Store.

        Args:
            rows: (list[str] | str) Rows can be a single JSON row (string) or an array of JSON strings.

        Typical example:
            feature_set.ingest_online('{"id": 1, "label": "Carl"}')

        Raises:
            Exception: Manual ingest online is not allowed on derived feature set.

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#online-ingestion
        """
        if self.is_derived():
            raise Exception("Manual ingest online is not allowed on derived feature set")

        if isinstance(rows, list):
            row_list = rows
        else:
            row_list = [rows]

        if self._online_ingestion_token is None or not self._online_ingestion_token.is_valid_for(
            self.id, self.major_version
        ):
            response: V1OnlineIngestionTokenResponse = self._stub.core_service_generate_ingest_token(
                feature_set_id=self.id, feature_set_version=self.version
            )
            self._online_ingestion_token = OnlineToken(
                self.id,
                self.major_version,
                response.token,
                response.signature,
                response.valid_to,
            )

        request = OnlineServiceOnlineIngestionBody(
            token=self._online_ingestion_token.token,
            signature=self._online_ingestion_token.signature,
            rows=row_list,
        )

        response = self._online_stub.online_service_online_ingestion(
            feature_set_id=self.id,
            feature_set_major_version=str(self.major_version),
            body=request,
        )
        return response

    def retrieve_online(self, *key) -> dict:
        """Retrieve data from the online Feature Store.

        Args:
            key: (Any) A specific primary key value for which the entry is obtained.

        Returns:
            dict: A dictionary of specific instance (JSON row).

            For example:

            {'id': '01', 'department': 'Engineering', 'name': 'Test'}

        Typical example:
            json = feature_set.retrieve_online(key)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#retrieving-from-online
        """
        if self._online_retrieval_token is None or not self._online_retrieval_token.is_valid_for(
            self.id, self.major_version
        ):
            response: V1OnlineRetrieveTokenResponse = self._stub.core_service_generate_online_retrieval_token(
                feature_set_id=self.id, feature_set_version=self.version
            )
            self._online_retrieval_token = OnlineToken(
                feature_set_id=self.id,
                feature_set_major_version=self.major_version,
                token=response.token,
                signature=response.signature,
                valid_to=response.valid_to,
            )

        response = self._online_stub.online_service_online_retrieve(
            feature_set_id=self.id,
            feature_set_major_version=str(self.major_version),
            token=self._online_retrieval_token.token,
            signature=self._online_retrieval_token.signature,
            key=list(map(lambda x: str(x), key)),
        )
        json_row = response.row

        return json.loads(json_row)

    def retrieve(self, start_date_time=None, end_date_time=None):
        """Retrieve data.

        This retrieves only a specific range of ingested data. If the parameters are empty,
        all data are fetched.

        Args:
            start_date_time: (str) A start date and time of the range of ingested data.
            end_date_time: (str) A end date and time of the range of ingested data.

        Returns:
            RetrieveHolder: Returns a link as output for reference.

        Typical example:
            ref = fs.retrieve(start_date_time="2023-01-01 00:00:00", end_date_time="2023-01-02 00:00:00")

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#retrieving-api
        """
        return RetrieveHolder(self._stub, self._feature_set, start_date_time, end_date_time, "")

    def start_online_offline_ingestion_async(self):
        """Create a job for feature set online to offline ingestion.

        Returns:
            IngestionJob: A job for online ingestion in case there is a new online data.
            It returns an error if there is nothing new to ingest from online.

            A job is created with a unique id and type Ingestion. For example:

            Job(id=<job_id>, type=Ingestion, done=False, childJobIds=[])

        Typical example:
            job = feature_set.start_online_offline_ingestion_async()
        """
        if self.is_derived():
            raise Exception("Online to offline ingest is not allowed on derived feature set")

        job_id = self._stub.core_service_start_online_offline_ingestion_job(
            feature_set_id=self._feature_set.id,
            feature_set_version=self._feature_set.version,
        )
        return IngestJob(self._stub, job_id)

    @interactive_console.record_stats
    def start_online_offline_ingestion(self):
        """Perform a feature set ingestion from online to offline store.

        This pushes new existing data from online Feature store into offline.

        Returns:
            A finished IngestionJob in case there was a new online data.
            It returns None if there was nothing new to ingest from online.

        Typical example:
            feature_set.online_offline_ingestion()

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_set_api.html#offline-to-online-api
        """
        job = self.start_online_offline_ingestion_async()
        return job.wait_for_result()

    def list_versions(self):
        """List all versions of a feature set.

        This shows all versions of a feature set (the current and previous ones).

        Returns:
            list[VersionDescription]: A list of versions and its details.

            For example:

            [{
              "version": "1.0",
              "versionChange": "Feature Set Created",
              "createdDateTime": "2023-01-01T00:00:00.000Z"
            }]

        Typical example:
            fs.list_versions()
        """
        response = self._stub.core_service_list_feature_set_versions(
            feature_set_id=self._feature_set.id,
        )
        return [VersionDescription(version) for version in response.versions]

    def get_version(self, version: str):
        """Obtain a specific version of current feature set.

        Args:
            version: (str) A specific version of feature set with format as "major.minor".

        Returns:
            FeatureSet: An existing feature set.

        Typical example:
            fs_different_version = feature_set.get(version)

        Raises:
            Exception: Version parameter must be in a format "major.minor".

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#obtaining-a-feature-set
        """
        if not re.search(r"^\d+\.\d+$", str(version)):
            raise Exception('Version parameter must be in a format "major.minor".')
        response = self._stub.core_service_get_feature_set(
            project_id=self._feature_set.project_id,
            feature_set_name=self._feature_set.feature_set_name,
            feature_set_version=str(version),
        )
        return FeatureSet(self._stub, self._online_stub, response.feature_set)

    def major_versions(self):
        """Return all major versions of a feature set.

        This shows all major versions of a feature set (the current and previous ones).

        Returns:
            list[FeatureSetMajorVersion]: A list of major versions and its details.

            For example:

            [{
              "version": "1.0",
              "versionChange": "Feature Set Created",
              "createdAt": "2023-01-01T00:00:00.000Z"
            }]

        Typical example:
            fs.list_versions()
        """
        response = self._stub.core_service_list_feature_set_versions(
            feature_set_id=self._feature_set.id
        )

        major_versions = []
        for version in response.versions:
            version_split = version.version.split(".")
            major_version = int(version_split[0])
            minor_version = int(version_split[1])
            if minor_version == 0:
                major_versions.append(
                    FeatureSetMajorVersion(
                        self._stub,
                        self.id,
                        major_version,
                        self.feature_set_name,
                        version.created_date_time,
                        version.version_change,
                    )
                )
        return major_versions

    @property
    def schema(self):
        return FeatureSetSchema(self._stub, self)

    def ingest_history(self):
        """Create an ingest history containing all ingestion.

        Returns:
            IngestHistory: An object of IngestHistory class.

        Typical example:
            history = my_feature_set.ingest_history()

        For more details:
            https://docs.h2o.ai/featurestore/api/ingest_history_api.html#getting-the-ingestion-history
        """
        return IngestHistory(self._stub, self._feature_set)

    def get_recommendations(self):
        """Get feature set recommendations.

        Returns:
            list[Recommendation]: A list of recommendations.

        Typical example:
            fs.get_recommendations()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#getting-recommendations
        """
        response = self._stub.core_service_get_recommendations(
            feature_set_id=self._feature_set.id
        )
        return [Recommendation(self._stub, self._online_stub, self, item) for item in response.matches]

    def schedule_ingest(
        self,
        name: str,
        source: DataSourceWrapper,
        schedule: str,
        description: str = "",
        credentials=None,
        allowed_failures=2,
    ):
        """Create a new scheduled task.

        Args:
            name: (str) A task name.
            source: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection)
              Source location of a supported data source.
            schedule: (str) Schedule should be in cron format.
            description: (str) Description about a task.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials)
              To access the provided data source. Default is None.
            allowed_failures: (int) The number of failures that can happen till the task gets paused to save resources.
              Any negative value has the meaning that failures are not tracked.
              Default is 2.

        Returns:
            ScheduledTask: A new scheduled task.

        Typical example:
            fs.schedule_ingest("task_name", source, schedule = "0 2 * * *", description = "", credentials = None)

        Raises:
            Exception: Scheduling Ingest with SparkDataFrame is not supported.

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_schedule.html#schedule-a-new-task
        """
        if source.is_local():
            raise Exception("Scheduling Ingest with local source is not supported.")
        else:
            data_source = source.get_raw_data_location(self._stub)

        client_timezone = tzlocal.get_localzone_name()

        request = V1ScheduleTaskRequest(
            name=name,
            description=description,
            feature_set_id=self._feature_set.id,
            project_id=self._feature_set.project_id,
            source=data_source,
            schedule=schedule,
            feature_set_version=self._feature_set.version,
            cron_time_zone=client_timezone,
            allowed_failures=allowed_failures if allowed_failures >= 0 else -1,
        )
        CredentialsHelper.set_credentials(request, data_source, credentials)
        scheduled_task = ScheduledTasks(self._stub, self)
        return scheduled_task.create_ingest_task(request)

    @property
    def schedule(self):
        return ScheduledTasks(self._stub, self)

    def get_preview(self):
        """Preview the returned data.

        This previews up to a maximum of 100 rows and 50 features.

        Returns:
            list[dict]: A list of dictionary which contains JSON rows.

        Typical example:
            fs.get_preview()
        """
        response = self._stub.core_service_get_feature_set_preview(
            feature_set_id=self._feature_set.id,
            feature_set_version=self._feature_set.version,
        )
        if response.preview_url:
            json_response = Utils.fetch_preview_as_json_array(response.preview_url)
            return json_response
        else:
            return []

    def ingest_lazy(self, source, credentials=None):
        """Ingest data lazy.

        Args:
            source: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials)
              To access the provided data source. Default is None.

        Returns:
            ScheduledTask: A new scheduled task.

        Typical example:
            fs.ingest_lazy(source)

        Raises:
            Exception: Lazy Ingest with SparkDataFrame is not supported.
        """
        if source.is_local():
            raise Exception("Lazy Ingest on local source is not supported.")
        else:
            data_source = source.get_raw_data_location(self._stub)
        request = V1ScheduleTaskRequest(
            feature_set_id=self._feature_set.id,
            project_id=self._feature_set.project_id,
            source=data_source,
            feature_set_version=self._feature_set.version,
        )
        CredentialsHelper.set_credentials(request, data_source, credentials)
        scheduled_task = ScheduledTasks(self._stub, self)
        scheduled_task.create_lazy_ingest_task(request)
        logging.info(f"Lazy ingest scheduled for feature set {self._feature_set.id}")

    def list_features_used_as_target_variable(self):
        response = self._stub.core_service_list_target_features(
            feature_set_id=self._feature_set.id,
            feature_set_version=self._feature_set.version,
        )
        return [feature.feature_name for feature in response.features]

    def list_owners(self):
        return self._list_users(V1PermissionType("Owner"))

    def list_editors(self):
        return self._list_users(V1PermissionType("Editor"))

    def list_consumers(self):
        return self._list_users(V1PermissionType("Consumer"))

    def list_sensitive_consumers(self):
        return self._list_users(V1PermissionType("SensitiveConsumer"))

    def list_viewers(self):
        return self._list_users(V1PermissionType("Viewer"))

    def _list_users(self, permission: V1PermissionType):
        args = {
            "resource_id": self._feature_set.id,
            "permission_filter": str(permission)
        }
        while args:
            response = self._stub.core_service_get_user_feature_set_permissions(**args)
            if response.next_page_token:
                args["page_token"] = response.next_page_token
            else:
                args = {}
            for user_with_permissions in response.users:
                yield UserWithPermission(user_with_permissions)

    def _get_job(self, job_id):
        return self._stub.core_service_get_job(job_id)

    def pin(self):
        self._stub.core_service_pin_feature_set(feature_set_id=self._feature_set.id)

    def unpin(self):
        self._stub.core_service_unpin_feature_set(feature_set_id=self._feature_set.id)

    @property
    def artifacts(self):
        return Artifacts(self._feature_set, self._stub)

    def get_derived_feature_sets(self):
        """List of derived feature sets that were build upon this feature set."""
        response = self._stub.core_service_get_feature_sets_derived_from(
            feature_set_id=self._feature_set.id, feature_set_major_version=str(self.major_version)
        )
        return [
            FeatureSet.from_listable_feature_set(self._stub, self._online_stub, listable_feature_set)
            for listable_feature_set in response.listable_feature_sets
        ]

    def get_parent_feature_sets(self):
        """List of feature sets this feature set was derived from."""
        base_feature_sets = []

        for versioned_id in self._feature_set.derived_from.feature_set_ids:
            base_fs = self._stub.core_service_get_feature_sets_last_minor_for_current_major(
                feature_set_id=versioned_id.id, feature_set_version=str(versioned_id.major_version) + ".0"
            ).feature_set
            base_feature_sets.append(FeatureSet(self._stub, self._online_stub, base_fs))

        return base_feature_sets

    def open_website(self):
        page = f"/feature-set/{self.id}/version/{self.version}"
        Browser(self._stub).open_website(page)

    @interactive_console.record_stats
    def optimize_storage(self, optimization=None):
        """Optimize storage of the feature set.

        By default, calls Z-order-by storage optimization for primary key(s)

        Args:
            optimization: (StorageOptimization) A specification of the optimization to be performed.

        Returns:
            StorageOptimizationResponse object containing metrics of the performed optimization.

        Typical example:
            fs.optimize_storage()
            fs.optimize_storage(ZOrderByOptimization(["name"]))

         For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html
        """
        job = self.optimize_storage_async(optimization)
        return job.wait_for_result()

    def optimize_storage_async(self, optimization=None):
        """Create a job for feature set data storage optimization.

        Args:
            optimization: (StorageOptimization) A specification of the optimization to be performed.

        Returns:
            OptimizeStorageJob: A job for optimization.

        Typical example:
            job_id = feature_set.optimize_storage_async()
        """
        request = V1StartOptimizeStorageJobRequest()
        request.feature_set_id = self._feature_set.id
        request.feature_set_version = self._feature_set.version
        if not optimization:
            optimization = self._create_default_storage_optimization()
        request.optimization = optimization._to_proto()

        job_id = self._stub.core_service_start_optimize_storage_job(body=request)
        return OptimizeStorageJob(self._stub, job_id)

    def _create_default_storage_optimization(self):
        if not self.primary_key:
            raise Exception("Can't create default optimization as primary key(s) is not defined")
        return ZOrderByOptimization(self.primary_key)

    @property
    def storage_optimization(self):
        """Returns storage optimization applied to current feature set version.

        Returns:
            An object of StorageOptimization class.

        Typical example:
            current_optimization = fs.storage_optimization
        """
        return StorageOptimization.from_proto(self._feature_set.storage_optimization)

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature_set)

    def __str__(self):
        return (
            f"Feature set name    : {self.feature_set_name} \n"
            f"Description         : {self.description} \n"
            f"Version             : {self.version} \n"
            f"Author                \n{Utils.output_indent_spacing(str(self.author), '      ')}"
            f"Project name        : {self.project} \n"
            f"Primary key         : {self.primary_key} \n"
            f"Feature set type    : {self.feature_set_type} \n"
            f"Created             : {self.created_date_time} \n"
            f"Last updated        : {self.last_update_date_time} \n"
            f"Sensitive           : {self.special_data._fs._feature_set.special_data.sensitive} \n"
            f"Time travel column  : {self.time_travel_column} \n"
            f"Features            : {self._custom_feature_fields()} \n"
            f"Tags                : {self.tags} \n"
            f"Partition by        : {self.partition_by} \n"
            f"Feature classifiers : {self.feature_classifiers} \n"
        )

    def _custom_feature_fields(self):
        tmp_dict = dict()
        for feature in self.features:
            tmp_dict.update({feature: self.features.get(feature).data_type})
        return json.dumps(tmp_dict, indent=5)


class VersionDescription:
    def __init__(self, version_description):
        self._version_description = version_description

    def __repr__(self):
        return Utils.pretty_print_proto(self._version_description)

    def __str__(self):
        return (
            f"Version           : {Utils.proto_to_dict(self._version_description).get('version')} \n"
            f"Version change    : {Utils.proto_to_dict(self._version_description).get('version_change')} \n"
            f"Created           : {Utils.proto_to_dict(self._version_description).get('created_date_time')} \n"
        )


class FeatureSetMajorVersion:
    def __init__(self, stub: CoreServiceApi, feature_set_id, feature_set_major_version, feature_set_name, created_at, version_change):
        self._stub = stub
        self.feature_set_id = feature_set_id
        self.feature_set_major_version = feature_set_major_version
        self.feature_set_name = feature_set_name
        self.created_at = created_at
        self.version_change = version_change

    def delete(self, wait_for_completion=False):
        """Deletes feature set major version."""
        self._stub.core_service_delete_feature_set_version(
            feature_set_id=self.feature_set_id,
            feature_set_major_version=self.feature_set_major_version,
        )
        if wait_for_completion:
            while self._stub.core_service_feature_set_exists(
                feature_set_id=self.feature_set_id,
                feature_set_major_version=self.feature_set_major_version,
            ).exists:
                time.sleep(1)
                logging.debug(
                    f"Waiting for feature set '{self.feature_set_name}' "
                    f"version '{self.feature_set_major_version}' deletion..."
                )
        logging.info(f"Feature set '{self.feature_set_name}' version '{self.feature_set_major_version}' is deleted")

    def __repr__(self):
        return json.dumps(
            {
                "version": self.feature_set_major_version,
                "versionChange": self.version_change,
                "createdAt": Utils.timestamp_to_string(self.created_at),
            }
        )

    def __str__(self):
        return (
            f"Version           : {self.feature_set_major_version} \n"
            f"Version change    : {self.version_change} \n"
            f"Created           : {Utils.timestamp_to_string(self.created_at)} \n"
        )


class TimeToLive:
    def __init__(self, stub: CoreServiceApi, feature_set):
        self._stub = stub
        self._fs = feature_set

    @property
    def ttl_offline(self):
        return self._fs._feature_set.time_to_live.ttl_offline

    @ttl_offline.setter
    def ttl_offline(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._fs._feature_set.version,
            time_to_live_offline_interval=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_TTL_OFFLINE")],
        )
        self._fs._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._fs._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def ttl_offline_interval(self):
        return self._fs._feature_set.time_to_live.ttl_offline_interval

    @ttl_offline_interval.setter
    def ttl_offline_interval(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._fs._feature_set.version,
            time_to_live_offline_interval_unit=V1OfflineTimeToLiveInterval(
                value
            ),
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_TTL_OFFLINE")],
        )
        self._fs._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._fs._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def ttl_online(self):
        return self._fs._feature_set.time_to_live.ttl_online

    @ttl_online.setter
    def ttl_online(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._fs._feature_set.version,
            time_to_live_online_interval=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_TTL_ONLINE")],
        )
        self._fs._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._fs._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def ttl_online_interval(self):
        return self._fs._feature_set.time_to_live.ttl_online_interval

    @ttl_online_interval.setter
    def ttl_online_interval(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._fs._feature_set.version,
            time_to_live_online_interval_unit=V1OnlineTimeToLiveInterval(
                value
            ),
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_TTL_ONLINE_INTERVAL")],
        )
        self._fs._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._fs._feature_set.id,
            body=update_request).updated_feature_set

    def __repr__(self):
        return Utils.pretty_print_proto(self._fs._feature_set.time_to_live)

    def __str__(self):
        return (
            f"ttl offline           : {self.ttl_offline} \n"
            f"ttl online            : {self.ttl_online} \n"
            f"ttl offline interval  : {self.ttl_offline_interval} \n"
            f"ttl online interval   : {self.ttl_online_interval} \n"
        )


class FeatureSetScope:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._scope = self._feature_set.time_travel_scope

    @property
    def start_date_time(self):
        return Utils.timestamp_to_string(self._scope.start_date_time)

    @property
    def end_date_time(self):
        return Utils.timestamp_to_string(self._scope.end_date_time)

    def __repr__(self):
        return Utils.pretty_print_proto(self._scope)

    def __str__(self):
        return f"Start date & time : {self.start_date_time} \n" f"End date & time   : {self.end_date_time} \n"


class FeatureSetSpecialData:
    def __init__(self, stub: CoreServiceApi, feature_set):
        self._stub = stub
        self._fs = feature_set

    @property
    def spi(self):
        return self._fs._feature_set.special_data.spi

    @property
    def pci(self):
        return self._fs._feature_set.special_data.pci

    @property
    def rpi(self):
        return self._fs._feature_set.special_data.rpi

    @property
    def demographic(self):
        return self._fs._feature_set.special_data.demographic

    @property
    def legal(self):
        return Legal(self._stub, self._fs)

    def __repr__(self):
        return Utils.pretty_print_proto(self._fs._feature_set.special_data)

    def __str__(self):
        return (
            f"legal           \n{Utils.output_indent_spacing(str(self.legal), '    ')}"
            f"spi           : {self.spi} \n"
            f"pci           : {self.pci} \n"
            f"rpi           : {self.rpi} \n"
            f"demographic   : {self.demographic} \n"
            f"sensitive     : {Utils.proto_to_dict(self._fs._feature_set.special_data).get('sensitive')} \n"
        )


class Statistics:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._statistics = self._feature_set.statistics

    @property
    def data_latency(self):
        return self._statistics.data_latency

    @property
    def records_count(self):
        return self._statistics.records_count

    def __repr__(self):
        return Utils.pretty_print_proto(self._statistics)

    def __str__(self):
        return f"Data latency  : {self.data_latency} \n" f"Records count : {self.records_count} \n"


class Legal:
    def __init__(self, stub: CoreServiceApi, feature_set):
        self._stub = stub
        self._fs = feature_set

    @property
    def approved(self):
        return self._fs._feature_set.special_data.legal.approved

    @approved.setter
    def approved(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._fs._feature_set.version,
            legal_approved=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_SPECIAL_DATA_LEGAL_APPROVED")],
        )
        self._fs._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._fs._feature_set.id,
            body=update_request).updated_feature_set

    @property
    def approved_date(self):
        return Utils.timestamp_to_string(self._fs._feature_set.special_data.legal.approved_date)

    @property
    def notes(self):
        return self._fs._feature_set.special_data.legal.notes

    @notes.setter
    def notes(self, value):
        update_request = CoreServiceUpdateFeatureSetBody(
            feature_set_version=self._fs._feature_set.version,
            legal_approved=value,
            fields_to_update=[V1UpdatableFeatureSetField("FEATURE_SET_SPECIAL_DATA_LEGAL_NOTES")],
        )
        self._fs._feature_set = self._stub.core_service_update_feature_set(
            feature_set_id=self._fs._feature_set.id,
            body=update_request).updated_feature_set

    def __repr__(self):
        return Utils.pretty_print_proto(self._fs._feature_set.special_data.legal)

    def __str__(self):
        return f"Approved  : {self.approved} \n" f"Notes     : {self.notes} \n"


class Online:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._online = self._feature_set.online

    @property
    def online_namespace(self):
        return self._online.online_namespace

    @property
    def connection_type(self):
        return self._online.connection_type

    @property
    def topic(self):
        return self._online.topic

    def __repr__(self):
        return Utils.pretty_print_proto(self._online)

    def __str__(self):
        return (
            f"Online namespace  : {self.online_namespace} \n"
            f"Connection type   : {self.connection_type} \n"
            f"Topic             : {self.topic} \n"
        )
