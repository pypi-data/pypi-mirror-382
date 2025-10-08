from codecs import open
from os import path

from h2o_featurestore.core.access_modifier import AccessModifier
from h2o_featurestore.core.client import login
from h2o_featurestore.core.client import login_custom
from h2o_featurestore.core.client import login_pat
from h2o_featurestore.core.collections.classifiers import EmptyClassifier
from h2o_featurestore.core.collections.classifiers import RegexClassifier
from h2o_featurestore.core.collections.classifiers import SampleClassifier
from h2o_featurestore.core.data_source_wrappers import BigQueryTable
from h2o_featurestore.core.data_source_wrappers import CSVFile
from h2o_featurestore.core.data_source_wrappers import CSVFolder
from h2o_featurestore.core.data_source_wrappers import DeltaTable
from h2o_featurestore.core.data_source_wrappers import DeltaTableFilter
from h2o_featurestore.core.data_source_wrappers import JdbcTable
from h2o_featurestore.core.data_source_wrappers import JSONFile
from h2o_featurestore.core.data_source_wrappers import JSONFolder
from h2o_featurestore.core.data_source_wrappers import MongoDbCollection
from h2o_featurestore.core.data_source_wrappers import ParquetFile
from h2o_featurestore.core.data_source_wrappers import ParquetFolder
from h2o_featurestore.core.data_source_wrappers import PartitionOptions
from h2o_featurestore.core.data_source_wrappers import Proxy
from h2o_featurestore.core.data_source_wrappers import SnowflakeCursor
from h2o_featurestore.core.data_source_wrappers import SnowflakeTable
from h2o_featurestore.core.data_source_wrappers import SparkDataFrame
from h2o_featurestore.core.entities.advanced_search_option import AdvancedSearchOption
from h2o_featurestore.core.entities.backfill_option import BackfillOption
from h2o_featurestore.core.entities.feature import FeatureType
from h2o_featurestore.core.feature_set_flow import FeatureSetFlow
from h2o_featurestore.core.job_type import JobType
from h2o_featurestore.core.schema import FeatureSchema
from h2o_featurestore.core.schema import Schema
from h2o_featurestore.core.storage_optimization import CompactOptimization
from h2o_featurestore.core.storage_optimization import ZOrderByOptimization
from h2o_featurestore.core.transformations import DriverlessAIMOJO
from h2o_featurestore.core.transformations import JoinFeatureSets
from h2o_featurestore.core.transformations import JoinFeatureSetsType
from h2o_featurestore.core.transformations import SparkPipeline
from h2o_featurestore.core.user_credentials import AzureKeyCredentials
from h2o_featurestore.core.user_credentials import AzurePrincipalCredentials
from h2o_featurestore.core.user_credentials import AzureSasCredentials
from h2o_featurestore.core.user_credentials import GcpCredentials
from h2o_featurestore.core.user_credentials import MongoDbCredentials
from h2o_featurestore.core.user_credentials import PostgresCredentials
from h2o_featurestore.core.user_credentials import S3Credentials
from h2o_featurestore.core.user_credentials import SnowflakeCredentials
from h2o_featurestore.core.user_credentials import SnowflakeKeyPairCredentials
from h2o_featurestore.core.user_credentials import TeradataCredentials

__all__ = [
    "Client",
    "FeatureSchema",
    "Schema",
    "CSVFile",
    "CSVFolder",
    "JSONFile",
    "JSONFolder",
    "MongoDbCollection",
    "ParquetFile",
    "ParquetFolder",
    "SnowflakeTable",
    "JdbcTable",
    "PartitionOptions",
    "SnowflakeCursor",
    "DeltaTable",
    "DeltaTableFilter",
    "Proxy",
    "JSONFolder",
    "Schema",
    "SparkDataFrame",
    "AzureKeyCredentials",
    "AzureSasCredentials",
    "AzurePrincipalCredentials",
    "S3Credentials",
    "TeradataCredentials",
    "SnowflakeCredentials",
    "SnowflakeKeyPairCredentials",
    "PostgresCredentials",
    "MongoDbCredentials",
    "SparkPipeline",
    "DriverlessAIMOJO",
    "JoinFeatureSetsType",
    "JoinFeatureSets",
    "EmptyClassifier",
    "RegexClassifier",
    "SampleClassifier",
    "BackfillOption",
    "FeatureSetFlow",
    "AdvancedSearchOption",
    "CompactOptimization",
    "ZOrderByOptimization",
    "GcpCredentials",
    "BigQueryTable",
    "AccessModifier",
    "JobType",
]

def __get_version():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, "version.txt"), encoding="utf-8") as f:
        return f.read().strip()

__version__ = __get_version()
