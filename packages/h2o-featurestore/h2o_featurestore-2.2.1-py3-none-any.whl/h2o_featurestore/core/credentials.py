import logging
import os
from urllib.parse import urlparse

from h2o_featurestore.gen.model.v1_aws_credentials import V1AWSCredentials
from h2o_featurestore.gen.model.v1_credentials import V1Credentials
from h2o_featurestore.gen.model.v1_raw_data_location import V1RawDataLocation

from .user_credentials import AzureKeyCredentials
from .user_credentials import AzurePrincipalCredentials
from .user_credentials import AzureSasCredentials
from .user_credentials import GcpCredentials
from .user_credentials import MongoDbCredentials
from .user_credentials import PostgresCredentials
from .user_credentials import S3Credentials
from .user_credentials import SnowflakeCredentials
from .user_credentials import SnowflakeKeyPairCredentials
from .user_credentials import TeradataCredentials
from .utils import Utils


class CredentialsHelper:
    @staticmethod
    def set_credentials(request, raw_data_location, credentials):
        source = next((k for k in V1RawDataLocation.attribute_map.keys() if k in raw_data_location), None)
        if source == "csv":
            url_path = raw_data_location.csv.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "csv_folder":
            url_path = raw_data_location.csv_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "json_folder":
            url_path = raw_data_location.json_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "json":
            url_path = raw_data_location.json.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "parquet":
            url_path = raw_data_location.parquet.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "parquet_folder":
            url_path = raw_data_location.parquet_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "delta_table":
            url_path = raw_data_location.delta_table.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path, credentials)
        elif source == "snowflake":
            CredentialsHelper.set_snowflake_credentials(request, credentials)
        elif source == "jdbc_table":
            CredentialsHelper.set_jdbc_credentials(request, source.connection_url, credentials)
        elif source == "mongo_db":
            CredentialsHelper.set_mongodb_credentials(request, credentials)
        elif source == "google_big_query":
            CredentialsHelper.set_gcp_credentials(request, credentials)
        else:
            raise Exception("Unsupported external data spec!")

    @staticmethod
    def get_credentials_based_on_cloud(request, url_path, credentials):
        if url_path.lower().startswith("s3"):
            CredentialsHelper.set_s3_credentials(request, credentials)
        elif url_path.lower().startswith("wasb") or url_path.lower().startswith("abfs"):
            CredentialsHelper.set_azure_credentials(request, url_path, credentials)
        elif url_path.lower().startswith("http"):
            pass
        elif url_path.lower().startswith("drive:"):
            CredentialsHelper.set_drive_credentials(request, url_path, credentials)
        elif url_path.lower().startswith("gs:"):
            CredentialsHelper.set_gcp_credentials(request, credentials)
        else:
            raise Exception("Unsupported external data spec!")

    @staticmethod
    def set_azure_credentials(request, url_path, credentials):
        sas_container = urlparse(url_path).netloc.split("@")[0]
        if credentials is None:
            account_name = Utils.read_env("AZURE_ACCOUNT_NAME", "Azure")
            account_key = os.getenv("AZURE_ACCOUNT_KEY")
            sas_token = os.getenv("AZURE_SAS_TOKEN")
            sp_client_id = os.getenv("AZURE_SP_CLIENT_ID")
            sp_tenant_id = os.getenv("AZURE_SP_TENANT_ID")
            sp_secret = os.getenv("AZURE_SP_SECRET")
            if account_key:
                credentials = AzureKeyCredentials(account_name, account_key)
            elif sas_token:
                credentials = AzureSasCredentials(account_name, sas_token)
            elif sp_client_id and sp_tenant_id and sp_secret:
                credentials = AzurePrincipalCredentials(account_name, sp_client_id, sp_tenant_id, sp_secret)
            else:
                raise Exception(
                    "Either Azure Key, SAS token or Service Credentials environment variable must be specified "
                    "to read from Azure data source!"
                )
        elif not isinstance(
            credentials,
            (AzureKeyCredentials, AzureSasCredentials, AzurePrincipalCredentials),
        ):
            raise Exception(
                "Credentials are not of type AzureKeyCredentials, AzureSasCredentials or AzurePrincipalCredentials!"
            )

        request.cred.azure.account_name = credentials.account_name
        if isinstance(credentials, AzureKeyCredentials):
            request.cred.azure.account_key = credentials.account_key
        if isinstance(credentials, AzureSasCredentials):
            request.cred.azure.sas_token = credentials.sas_token
            request.cred.azure.sas_container = sas_container
        if isinstance(credentials, AzurePrincipalCredentials):
            request.cred.azure.sp_client_id = credentials.client_id
            request.cred.azure.sp_tenant_id = credentials.tenant_id
            request.cred.azure.sp_secret = credentials.secret

    @staticmethod
    def set_s3_credentials(request, credentials):
        if credentials is None:
            if os.environ.get("S3_ACCESS_KEY"):
                access_key = Utils.read_env("S3_ACCESS_KEY", "S3")
            elif os.environ.get("AWS_ACCESS_KEY_ID"):
                access_key = Utils.read_env("AWS_ACCESS_KEY_ID", "S3")
            else:
                access_key = None
            if os.environ.get("S3_SECRET_KEY"):
                secret_key = Utils.read_env("S3_SECRET_KEY", "S3")
            elif os.environ.get("AWS_SECRET_ACCESS_KEY"):
                secret_key = Utils.read_env("AWS_SECRET_ACCESS_KEY", "S3")
            else:
                secret_key = None
            if os.environ.get("S3_REGION"):
                region = Utils.read_env("S3_REGION", "S3")
            elif os.environ.get("AWS_DEFAULT_REGION"):
                region = Utils.read_env("AWS_DEFAULT_REGION", "S3")
            else:
                region = None
            if os.environ.get("S3_ROLE_ARN"):
                role_arn = Utils.read_env("S3_ROLE_ARN", "S3")
            elif os.environ.get("AWS_ROLE_ARN"):
                role_arn = Utils.read_env("AWS_ROLE_ARN", "S3")
            else:
                role_arn = None
            if os.environ.get("S3_SESSION_TOKEN"):
                session_token = Utils.read_env("S3_SESSION_TOKEN", "S3")
            elif os.environ.get("AWS_SESSION_TOKEN"):
                session_token = Utils.read_env("AWS_SESSION_TOKEN", "S3")
            else:
                session_token = None
            if os.environ.get("S3_ENDPOINT"):
                endpoint = Utils.read_env("S3_ENDPOINT", "S3")
            elif os.environ.get("AWS_ENDPOINT_URL"):
                endpoint = Utils.read_env("AWS_ENDPOINT_URL", "S3")
            else:
                endpoint = None

            if access_key and secret_key:
                credentials = S3Credentials(access_key, secret_key, region, endpoint, role_arn, session_token)
            else:
                try:
                    profile = Utils.read_env("AWS_PROFILE", "S3")
                except Exception:
                    logging.warning("AWS_PROFILE is not found in the environment. Profile is set to 'default'.")
                    profile = "default"
                credentials = S3Credentials.from_profile(profile)
                if credentials is None:
                    credentials = S3Credentials(access_key="PUBLIC_ONLY", secret_key="PUBLIC_ONLY")

        if not isinstance(credentials, S3Credentials):
            raise Exception("Credentials is not of type S3Credentials!")

        request.cred = V1Credentials(
            aws=V1AWSCredentials(
                access_token=credentials.access_token,
                secret_token=credentials.secret_token,
            )
        )

        if credentials.session_token:
            request.cred.aws.session_token = credentials.session_token
        if credentials.region:
            request.cred.aws.region = credentials.region
        if credentials.role_arn:
            request.cred.aws.role_arn = credentials.role_arn
        if credentials.endpoint:
            request.cred.aws.endpoint = credentials.endpoint

    @staticmethod
    def set_snowflake_credentials(request, credentials):
        if credentials is None:
            if os.environ.get("SNOWFLAKE_USER"):
                user = Utils.read_env("SNOWFLAKE_USER", "Snowflake")
            else:
                user = None
            if os.environ.get("SNOWFLAKE_PASSWORD"):
                password = Utils.read_env("SNOWFLAKE_PASSWORD", "Snowflake")
            else:
                password = None
            if os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE"):
                private_key_file = Utils.read_env("SNOWFLAKE_PRIVATE_KEY_FILE", "Snowflake")
            else:
                private_key_file = None
            if os.environ.get("PRIVATE_KEY_PASSPHRASE"):
                passphrase = Utils.read_env("PRIVATE_KEY_PASSPHRASE", "Snowflake")
            else:
                passphrase = None

            if user and password:
                credentials = SnowflakeCredentials(user=user, password=password)
            elif user and private_key_file:
                credentials = SnowflakeKeyPairCredentials(
                    user=user, private_key_file=private_key_file, passphrase=passphrase
                )
            else:
                raise Exception(
                    "SNOWFLAKE_USER and either SNOWFLAKE_PASSWORD or SNOWFLAKE_PRIVATE_KEY_FILE"
                    " environment variables must be specified to read from Snowflake data source!"
                )

        request.cred.snowflake.user = credentials.user
        if isinstance(credentials, SnowflakeCredentials):
            request.cred.snowflake.password = credentials.password
        if isinstance(credentials, SnowflakeKeyPairCredentials):
            pem_private_key = CredentialsHelper.read_private_key_pem_file(credentials.private_key_file)
            request.cred.snowflake.pem_private_key = pem_private_key
            if credentials.passphrase:
                request.cred.snowflake.passphrase = credentials.passphrase

    @staticmethod
    def set_jdbc_credentials(request, connection_url, credentials):
        database_type = connection_url.split(":")[1]
        if credentials is None:
            if database_type == "teradata":
                credentials = TeradataCredentials(
                    user=Utils.read_env("JDBC_TERADATA_USER", "JDBC Teradata"),
                    password=Utils.read_env("JDBC_TERADATA_PASSWORD", "JDBC Teradata"),
                )
            elif database_type == "postgres":
                credentials = PostgresCredentials(
                    user=Utils.read_env("JDBC_POSTGRES_USER", "JDBC Postgres"),
                    password=Utils.read_env("JDBC_TERADATA_PASSWORD", "JDBC Postgres"),
                )
            else:
                raise Exception("Invalid database type, supported types are: teradata, postgres")
        elif not isinstance(credentials, (TeradataCredentials, PostgresCredentials)):
            raise Exception("Credentials are not of type TeradataCredentials or PostgresCredentials!")
        request.cred.jdbc_database.user = credentials.user
        request.cred.jdbc_database.password = credentials.password

    @staticmethod
    def set_mongodb_credentials(request, credentials):
        if credentials is None:
            credentials = MongoDbCredentials(
                user=Utils.read_env("MONGODB_USER", "MongoDB"),
                password=Utils.read_env("MONGODB_PASSWORD", "MongoDB"),
            )
        elif not isinstance(credentials, MongoDbCredentials):
            raise Exception("Credentials are not of type MongoDbCredentials!")
        request.cred.mongo_db.user = credentials.user
        request.cred.mongo_db.password = credentials.password

    @staticmethod
    def read_private_key_pem_file(pem_file):
        with open(pem_file, "rb") as key:
            return key.read()

    @staticmethod
    def set_drive_credentials(request, url_path, credentials):
        if credentials is not None:
            logging.warning("Credentials were ignored, they are not needed for accessing H2O Drive")

        request.cred.drive.SetInParent()

    @staticmethod
    def set_gcp_credentials(request, credentials):
        if credentials is None:
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                credentials_path = Utils.read_env("GOOGLE_APPLICATION_CREDENTIALS", "GCP")
                credentials = GcpCredentials.from_file(credentials_path)
            else:
                raise Exception(
                    "GOOGLE_APPLICATION_CREDENTIALS environment variable must be specified"
                    "to read from GCP data source!"
                )

        if not isinstance(credentials, GcpCredentials):
            raise Exception("Credentials are not of type GcpCredentials!")

        request.cred.gcp.credentials_file_content = credentials.credentials_file_content
