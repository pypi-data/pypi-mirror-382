import logging
from copy import deepcopy
from typing import Optional

from h2o_featurestore.core import interactive_console
from h2o_featurestore.core.acl import AccessControlList
from h2o_featurestore.core.auth import AuthWrapper
from h2o_featurestore.core.auth.token_api_client import TokenApiClient
from h2o_featurestore.core.collections.admin_projects import AdminProjects
from h2o_featurestore.core.collections.classifiers import Classifiers
from h2o_featurestore.core.collections.feature_set_reviews import FeatureSetReviews
from h2o_featurestore.core.collections.jobs import Jobs
from h2o_featurestore.core.collections.projects import Projects
from h2o_featurestore.core.config_utils import ConfigUtils
from h2o_featurestore.core.connection_config import ConnectionConfig
from h2o_featurestore.core.credentials import CredentialsHelper
from h2o_featurestore.core.dashboard import Dashboard
from h2o_featurestore.core.data_source_wrappers import DataSourceWrapper
from h2o_featurestore.core.entities.component_versions import ComponentVersions
from h2o_featurestore.core.entities.extract_schema_job import ExtractSchemaJob
from h2o_featurestore.core.schema import Schema
from h2o_featurestore.core.utils import StorageSession
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.api.online_service_api import OnlineServiceApi
from h2o_featurestore.gen.configuration import Configuration
from h2o_featurestore.gen.model.v1_derived_information import V1DerivedInformation
from h2o_featurestore.gen.model.v1_start_extract_schema_job_request import (
    V1StartExtractSchemaJobRequest,
)
from h2o_featurestore.gen.model.v1_versioned_id import V1VersionedId


class FeatureStoreClient:
    """FeatureStoreClient manages feature stores."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
        storage_use_ca_cert: bool = False,
    ):
        """Initializes Feature Store Client.
        Do not initialize manually, use `h2o_featurestore.login()` instead.

        Args:
            connection_config (ConnectionConfig): AIEM connection configuration object.
            verify_ssl: Set to False to disable SSL certificate verification.
            ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
            storage_use_ca_cert: Whether to use `verify_ssl` and `ssl_ca_cert` options when connecting to the underlying object storage.
        """
        print("Initializing Feature Store Client with connection config:")
        print(connection_config.featurestore_url)

        if storage_use_ca_cert:
            # Configure global storage session with SSL settings
            StorageSession.configure(verify_ssl=verify_ssl, ssl_ca_cert=ssl_ca_cert)

        configuration = Configuration(host=connection_config.featurestore_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert
        self._config = ConfigUtils.collect_properties()

        with TokenApiClient(
            configuration, connection_config.token_provider
        ) as core_service_api_client:
            self._stub = CoreServiceApi(core_service_api_client)
            

            response = self._stub.core_service_get_api_config()
            online_config = Configuration(host=response.public_online_rest_api_url)
            online_config.verify_ssl = verify_ssl
            online_config.ssl_ca_cert = ssl_ca_cert

            # Initialize online API client
            with TokenApiClient(
                online_config, connection_config.token_provider
            ) as online_api_client:
                self.online_api = OnlineServiceApi(online_api_client)
            admin_projects = AdminProjects(self._stub, self.online_api)
            self.projects = Projects(
                self._stub,
                self.online_api,
                admin_projects
            )
            self.jobs = Jobs(self._stub)
            self.classifiers = Classifiers(self._stub)
            self.acl = AccessControlList(self._stub, online_api_client)
            self.feature_set_reviews = FeatureSetReviews(self._stub, online_api_client)
            self.dashboard = Dashboard(self._stub, online_api_client)
            self.auth = AuthWrapper(self._stub)

            self._check_client_vs_server_version(self.get_version())

    def _get_server_version(self) -> str:
        response = self._stub.core_service_get_version()
        return response.version


    def get_version(self) -> ComponentVersions:
        """Return Feature Store component versions."""
        return ComponentVersions(self._get_client_version(), self._get_server_version())

    @staticmethod
    def _get_client_version() -> str:
        """Return the client version."""
        from h2o_featurestore import __version__ as client_version
        return client_version

    def extract_schema_from_source_async(
        self, raw_data_location: DataSourceWrapper, credentials=None
    ) -> ExtractSchemaJob:
        """Create a schema extract job.

        This generates a new job for schema extraction from a provided data source.

        Args:
            raw_data_location: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection | BigQueryTable)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials| GcpCredentials)
              To access the provided data source. Default is None.

        Returns:
            ExtractSchemaJob: A job for schema extraction.

            A job is created with unique id and type ExtractSchema. For example:

            Job(id=<job_id>, type=ExtractSchema, done=False, childJobIds=[])

        For more details:
            Supported data sources:
              https://docs.h2o.ai/featurestore/supported_data_sources.html#supported-data-sources

            Passing credentials as parameters: An example
              https://docs.h2o.ai/featurestore/api/client_credentials.html#passing-credentials-as-a-parameters
        """
        request = V1StartExtractSchemaJobRequest()
        data_source = raw_data_location.get_raw_data_location(self._stub)
        request.raw_data = deepcopy(data_source)
        if not raw_data_location.is_local():
            CredentialsHelper.set_credentials(request, data_source, credentials)
        job_id = self._stub.core_service_start_extract_schema_job(body=request)
        return ExtractSchemaJob(self._stub, job_id)

    @interactive_console.record_stats
    def extract_schema_from_source(self, raw_data_location, credentials=None) -> Schema:
        """Extract a schema from a data source.

        Args:
            raw_data_location: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials)
              To access the provided data source. Default is None.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical usage example:

            credentials = S3Credentials(access_key, secret_key, region=None, endpoint=None, role_arn=None)
            source = CSVFile(path, delimiter=",")
            schema = Client(...).extract_schema_from_source(source, credentials)

        For more details:
            Supported data sources:
              https://docs.h2o.ai/featurestore/supported_data_sources.html#supported-data-sources

            Passing credentials as parameters: An example
              https://docs.h2o.ai/featurestore/api/client_credentials.html#passing-credentials-as-a-parameters
        """
        job = self.extract_schema_from_source_async(raw_data_location, credentials)
        return job.wait_for_result()

    @interactive_console.record_stats
    def extract_derived_schema(self, feature_sets, transformation) -> Schema:
        """Create a schema from an existing feature set using a selected transformation.

        Args:
            feature_sets: (list(str)) A list of existing feature sets.
            transformation: (Transformation) Represents an instance of Transformation.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical usage example:

            import featurestore.transformations as t
            spark_pipeline_transformation = t.SparkPipeline("...")
            schema = Client(...).extract_derived_schema([parent_feature_set], spark_pipeline_transformation)

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-derived-schema-from-a-parent-feature-set-with-applied-transformation
        """
        job = self.extract_derived_schema_async(feature_sets, transformation)
        return job.wait_for_result()

    def extract_derived_schema_async(self, feature_sets, transformation) -> ExtractSchemaJob:
        """Create a schema extract job.

        This generates the new job for schema extraction from an existing feature set using
        selected transformation.

        Args:
            feature_sets: (list[str]) A list of existing feature sets.
            transformation: (Transformation) Represents an instance of Transformation.
              Find the supported transformations in more details section.

        Returns:
            ExtractSchemaJob: A job for schema extraction.

            A job is created with unique id and type ExtractSchema. For example:

            Job(id=<job_id>, type=ExtractSchema, done=False, childJobIds=[])

        For more details:
            Supported derived transformation:
              https://docs.h2o.ai/featurestore/supported_derived_transformation.html#supported-derived-transformation
        """
        transformation._initialize(self._stub)
        request = V1StartExtractSchemaJobRequest(
            derived_from=V1DerivedInformation(
                feature_set_ids=[V1VersionedId(id=f.id, major_version=f.major_version) for f in feature_sets],
                transformation=transformation._to_proto(),
            )
        )

        job_id = self._stub.core_service_start_extract_schema_job(request)
        return ExtractSchemaJob(self._stub, job_id)

    def _has_online_retrieve_permissions(self, project_name, feature_set_name):
        response = self._stub.core_service_has_permission_to_retrieve(
            project_name=project_name,
            feature_set_name=feature_set_name
        )
        return response.has_retrieve_permission

    def show_progress(self, interactive):
        """Enable or disable interactive logging. Logging is enabled by default.

        Args:
            interactive: (bool) If True, enables interactive logging.

        Typical usage example:
            client.show_progress(False)
        """
        ConfigUtils.set_property(self._config, ConfigUtils.INTERACTIVE_LOGGING, str(interactive))

    @staticmethod
    def _check_client_vs_server_version(component_versions):
        logging.info(f"Server version: {component_versions.server_version}")
        logging.info(f"Client version: {component_versions.client_version}")

        if component_versions.client_is_newer_than_server():
            logging.warning(
                f"""\
The client version ({component_versions.client_version}) is newer then server version ({component_versions.server_version}).
It's recommended to downgrade the client. Otherwise, an UNIMPLEMENTED exception will be thrown in case
that a new method (not supported by server) were utilized."""
            )
        elif component_versions.server_is_newer_than_client():
            logging.warning(
                f"""\
The client version ({component_versions.client_version}) is older then server version ({component_versions.server_version}).
It's recommended to upgrade the client."""
            )
