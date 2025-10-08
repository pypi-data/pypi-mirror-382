import base64
import configparser
import logging
import os


class AzureKeyCredentials:
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key


class AzureSasCredentials:
    def __init__(self, account_name, sas_token):
        self.account_name = account_name
        self.sas_token = sas_token


class AzurePrincipalCredentials:
    def __init__(self, account_name, client_id, tenant_id, secret):
        self.account_name = account_name
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.secret = secret


class S3Credentials:
    def __init__(self, access_key, secret_key, region=None, endpoint=None, role_arn=None, session_token=None):
        if region is None:
            logging.warning("AWS region is not configured. Using 'us-east-1'.")
            self.region = "us-east-1"
        else:
            self.region = region
        self.access_token = access_key
        self.secret_token = secret_key
        self.session_token = session_token

        self.role_arn = role_arn
        self.endpoint = endpoint

    @classmethod
    def from_profile(cls, profile):
        if os.path.isfile(os.path.join(os.path.expanduser("~"), ".aws/credentials")):
            config = configparser.RawConfigParser()
            config.read(os.path.join(os.path.expanduser("~"), ".aws/credentials"))
            aws_key = config.get(profile, "aws_access_key_id")
            aws_secret = config.get(profile, "aws_secret_access_key")
            aws_session = config.get(profile, "aws_session_token", fallback=None)
            config.read(os.path.join(os.path.expanduser("~"), ".aws/config"))
            profile_entry = "default" if profile == "default" else f"profile {profile}"
            role_arn = config.get(profile_entry, "role_arn", fallback=None)
            endpoint = config.get(profile_entry, "endpoint_url", fallback=None)
            aws_region = config.get(profile_entry, "region", fallback=None)

            return S3Credentials(
                access_key=aws_key,
                secret_key=aws_secret,
                session_token=aws_session,
                region=aws_region,
                role_arn=role_arn,
                endpoint=endpoint,
            )
        else:
            return None


class SnowflakeCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class SnowflakeKeyPairCredentials:
    def __init__(self, user, private_key_file, passphrase=None):
        self.user = user
        self.private_key_file = private_key_file
        self.passphrase = passphrase


class TeradataCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class PostgresCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class MongoDbCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class GcpCredentials:
    def __init__(self, credentials_file_content):
        self.credentials_file_content = credentials_file_content

    @classmethod
    def from_file(cls, file_path):
        with open(file_path) as credentials_file:
            content = credentials_file.read()
            credentials = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            return GcpCredentials(credentials)
