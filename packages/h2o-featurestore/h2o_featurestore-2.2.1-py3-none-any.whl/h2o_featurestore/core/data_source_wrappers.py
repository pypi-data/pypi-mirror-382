import os
import re
import tempfile
from abc import ABC
from abc import abstractmethod

import requests

from h2o_featurestore.core.utils import StorageSession
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.v1_big_query_table_spec import V1BigQueryTableSpec
from h2o_featurestore.gen.model.v1_csv_file_spec import V1CSVFileSpec
from h2o_featurestore.gen.model.v1_csv_folder_spec import V1CSVFolderSpec
from h2o_featurestore.gen.model.v1_delta_table_spec import V1DeltaTableSpec
from h2o_featurestore.gen.model.v1_filter import V1Filter
from h2o_featurestore.gen.model.v1_generate_temporary_upload_request import (
    V1GenerateTemporaryUploadRequest,
)
from h2o_featurestore.gen.model.v1_generate_temporary_upload_response import (
    V1GenerateTemporaryUploadResponse,
)
from h2o_featurestore.gen.model.v1_jdbc_table_spec import V1JDBCTableSpec
from h2o_featurestore.gen.model.v1_json_file_spec import V1JSONFileSpec
from h2o_featurestore.gen.model.v1_json_folder_spec import V1JSONFolderSpec
from h2o_featurestore.gen.model.v1_mongo_db_collection_spec import (
    V1MongoDbCollectionSpec,
)
from h2o_featurestore.gen.model.v1_parquet_file_spec import V1ParquetFileSpec
from h2o_featurestore.gen.model.v1_parquet_folder_spec import V1ParquetFolderSpec
from h2o_featurestore.gen.model.v1_raw_data_location import V1RawDataLocation
from h2o_featurestore.gen.model.v1_snowflake_table_spec import V1SnowflakeTableSpec
from h2o_featurestore.gen.models import V1BooleanFilter
from h2o_featurestore.gen.models import V1NumericalFilter
from h2o_featurestore.gen.models import V1TextualFilter

from .commons.spark_utils import SparkUtils
from .utils import Utils


class DataSourceWrapper(ABC):
    def is_local(self):
        return False

    def _write_to_storage(self, stub: CoreServiceApi, filter_pattern=""):
        pass

    @abstractmethod
    def get_raw_data_location(self, stub: CoreServiceApi):
        raise Exception("Not implemented")


class FileDataSourceWrapper(DataSourceWrapper, ABC):
    def __init__(self, path: str):
        self.path: str = path
        self._remote_path = None

    def is_local_file(self):
        if self.is_local():
            local_path = self.path.removeprefix("file://")
            return os.path.isfile(local_path)
        else:
            return False

    def is_local_directory(self):
        if self.is_local():
            local_path = self.path.removeprefix("file://")
            return os.path.isdir(local_path)
        else:
            return False

    def is_local(self):
        return self.path.lower().startswith("file://")

    def _write_to_storage(self, stub: CoreServiceApi, filter_pattern=""):
        if self._remote_path:
            return
        if not self.is_local():
            raise ValueError("Only local file can be written to temp storage")

        local_path = self.path.removeprefix("file://")
        if not os.path.exists(local_path):
            raise ValueError(f"Path {local_path} does not exist")
        files_with_md5_checksum = {}
        if self.is_local_file():
            if os.path.getsize(local_path) > 0:
                md5_checksum = Utils.generate_md5_checksum(local_path)
                files_with_md5_checksum = {os.path.basename(local_path): md5_checksum}
        elif not filter_pattern:
            for file in os.listdir(local_path):
                if os.path.getsize(os.path.join(local_path, file)) > 0:
                    md5_checksum = Utils.generate_md5_checksum(os.path.join(local_path, file))
                    files_with_md5_checksum[file] = md5_checksum
        else:
            segments = filter_pattern.rsplit("/", 1)
            file_pattern = re.compile(segments[1]) if len(segments) > 1 else re.compile(filter_pattern)
            path_pattern = re.compile(segments[0] + "$") if len(segments) > 1 else re.compile(".*")
            for dirpath, dirnames, filenames in os.walk(local_path):
                for fn in filenames:
                    if file_pattern.match(fn) and path_pattern.search(dirpath):
                        file_path = os.path.join(dirpath, fn)
                        rel_file_path = os.path.relpath(file_path, local_path)
                        md5_checksum = Utils.generate_md5_checksum(file_path)
                        files_with_md5_checksum[rel_file_path] = md5_checksum

        if not files_with_md5_checksum:
            if self.is_local_file():
                raise ValueError(f"File {local_path} is empty")
            else:
                raise ValueError(f"Directory {local_path} is empty")

        request = V1GenerateTemporaryUploadRequest(files_with_md5_checksum=files_with_md5_checksum)
        write_info: V1GenerateTemporaryUploadResponse = stub.core_service_generate_temporary_upload(request)
        for file, md5_checksum in files_with_md5_checksum.items():
            if self.is_local_file():
                absolute_path = local_path
            else:
                absolute_path = os.path.join(local_path, file)
            with open(absolute_path, "rb") as local_file:
                session = StorageSession.get_session()
                response = session.put(
                    url=write_info.file_responses[file].presign_url,
                    data=local_file,
                    headers=write_info.file_responses[file].headers,
                )
                if response.status_code not in range(200, 300):
                    raise Exception(
                        f"File upload {file} failed with status code {response.status_code} "
                        f"and message"
                        f" {response.text}"
                    )
        if self.is_local_file():
            self._remote_path = write_info.file_responses[os.path.basename(local_path)].url
        else:
            self._remote_path = write_info.directory_url

    @property
    def external_path(self):
        if self._remote_path:
            return self._remote_path
        else:
            return self.path


class DeltaTableFilter:
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value
        self._filter = self.__build()

    def __build(self):
        if isinstance(self.value, str):
            return V1Filter(text=V1TextualFilter(field=self.column, operator=self.operator, value=[self.value]))
        elif isinstance(self.value, (int, float)):
            return V1Filter(
                numeric=V1NumericalFilter(field=self.column, operator=self.operator, value=self.value)
            )
        elif isinstance(self.value, bool):
            return V1Filter(boolean=V1BooleanFilter(field=self.column, operator=self.operator, value=self.value))


class SparkDataFrame(DataSourceWrapper):
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self._write_path = None

    def is_local(self):
        return True

    def _write_to_storage(self, stub):
        if self._write_path:
            return

        from pyspark.sql import SparkSession  # type: ignore # Local import

        spark = SparkSession.builder.getOrCreate()

        SparkUtils.configure_user_spark(spark)
        spark.conf.set("spark.sql.session.timeZone", "UTC")
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = os.path.join(tmp, "dt")
            self.dataframe.write.parquet(output_dir)
            parquet_files = [file for file in os.listdir(output_dir) if file.endswith(".parquet")]
            files_with_md5_checksum = {}
            for file in parquet_files:
                md5_checksum = Utils.generate_md5_checksum(os.path.join(output_dir, file))
                files_with_md5_checksum[file] = md5_checksum

            request = V1GenerateTemporaryUploadRequest(files_with_md5_checksum=files_with_md5_checksum)
            write_info: V1GenerateTemporaryUploadResponse = stub.core_service_generate_temporary_upload(request)
            for file, md5_checksum in files_with_md5_checksum.items():
                with open(os.path.join(output_dir, file), "rb") as local_file:
                    session = StorageSession.get_session()
                    response = session.put(
                        url=write_info.file_responses[file].presign_url,
                        data=local_file,
                        headers=write_info.file_responses[file].headers,
                    )
                    if response.status_code not in range(200, 300):
                        raise Exception(
                            f"File upload {file} failed with status code {response.status_code} "
                            f"and message"
                            f" {response.text}"
                        )

            self._write_path = write_info.directory_url

    def get_raw_data_location(self, stub: CoreServiceApi):
        if not self._write_path:
            self._write_to_storage(stub)
        parquet = V1ParquetFileSpec(path=self._write_path)
        raw_data_location = V1RawDataLocation(parquet=parquet)
        return raw_data_location


class CSVFile(FileDataSourceWrapper):
    def get_raw_data_location(self, stub: CoreServiceApi):
        if self.is_local():
            self._write_to_storage(stub)

        csv = V1CSVFileSpec(path=self.external_path,
                            delimiter=self.delimiter)

        raw_data_location = V1RawDataLocation(csv=csv)
        return raw_data_location

    def __init__(self, path, delimiter=","):
        super().__init__(path)
        self.delimiter = delimiter


class JSONFile(FileDataSourceWrapper):
    def __init__(self, path, multiline=False):
        super().__init__(path)
        self.multiline = multiline

    def get_raw_data_location(self, stub: CoreServiceApi):
        if self.is_local():
            self._write_to_storage(stub)
        json = V1JSONFileSpec(path=self.external_path, multiline=self.multiline)
        raw_data_location = V1RawDataLocation(json=json)
        return raw_data_location


class ParquetFile(FileDataSourceWrapper):
    def __init__(self, path):
        super().__init__(path)

    def get_raw_data_location(self, stub: CoreServiceApi):
        if self.is_local():
            self._write_to_storage(stub)
        parquet = V1ParquetFileSpec(path=self.external_path)
        raw_data_location = V1RawDataLocation(parquet=parquet)
        return raw_data_location

class Proxy:
    def __init__(self, host="", port=0, user="", password=""):
        if port and not host:
            raise ValueError("Proxy port specified but host is missing!")
        if not port and host:
            raise ValueError("Proxy host specified but port is missing!")
        if port and host:
            if user and not password:
                raise ValueError("Proxy user specified but password is missing!")
            if not user and password:
                raise ValueError("Proxy password specified but user is missing!")
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class SnowflakeTable(DataSourceWrapper):
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        table="",
        query="",
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        if not (query or table):
            raise ValueError("table or query is required!")
        if query and table:
            raise ValueError("Only one of table or query is supported!")

        self.table = table
        self.database = database
        self.url = url
        self.query = query
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account

    def get_raw_data_location(self, stub: CoreServiceApi):
        raw_data_location = V1RawDataLocation()
        snowflake = V1SnowflakeTableSpec(
            table=self.table,
            database=self.database,
            url=self.url,
            warehouse=self.warehouse,
            schema=self.schema,
            query=self.query,
            insecure=self.insecure,
            role=self.role,
            account=self.account,
        )
        if self.proxy:
            snowflake.proxy.host = self.proxy.host
            snowflake.proxy.port = self.proxy.port
            snowflake.proxy.user = self.proxy.user
            snowflake.proxy.password = self.proxy.password
        raw_data_location = V1RawDataLocation(
            snowflake=snowflake
        )
        return raw_data_location


class JdbcTable(DataSourceWrapper):
    def __init__(
        self,
        connection_url,
        table="",
        query="",
        partition_options=None,
    ):
        if not (table or query):
            raise ValueError("Table or query is required!")
        if table and query:
            raise ValueError("Only one of table or query is supported!")
        self.table = table
        self.query = query
        self.connection_url = connection_url
        self.partition_options = partition_options

    def get_raw_data_location(self, stub: CoreServiceApi):

        jdbc = V1JDBCTableSpec(
            table=self.table,
            connection_url=self.connection_url,
            query=self.query,
        )
        if self.partition_options is not None:
            jdbc.num_partitions = self.partition_options.num_partitions
            jdbc.partition_column = self.partition_options.partition_column
            jdbc.lower_bound = self.partition_options.lower_bound
            jdbc.upper_bound = self.partition_options.upper_bound
            jdbc.fetch_size = self.partition_options.fetch_size
        raw_data_location = V1RawDataLocation(
            jdbc=jdbc
        )
        return raw_data_location


class PartitionOptions:
    def __init__(
        self,
        num_partitions=None,
        partition_column=None,
        lower_bound=None,
        upper_bound=None,
        fetch_size=1000,
    ):
        self.num_partitions = num_partitions
        self.partition_column = partition_column
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fetch_size = fetch_size


class SnowflakeCursor(DataSourceWrapper):
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        cursor,
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        self.cursor = cursor
        self.database = database
        self.url = url
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account

    def get_raw_data_location(self, stub: CoreServiceApi):

        snowflake = V1SnowflakeTableSpec(
            table="",
            database=self.database,
            url=self.url,
            warehouse=self.warehouse,
            schema=self.schema,
            query=self.get_latest_query(),
            insecure=self.insecure,
            role=self.role,
            account=self.account,
        )
        if self.proxy:
            snowflake.proxy.host = self.proxy.host
            snowflake.proxy.port = self.proxy.port
            snowflake.proxy.user = self.proxy.user
            snowflake.proxy.password = self.proxy.password
        raw_data_location = V1RawDataLocation(
            snowflake=snowflake
        )
        return raw_data_location

    def get_latest_query(self):
        query = (
            "SELECT QUERY_TEXT::VARCHAR "
            "FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_SESSION(RESULT_LIMIT => 10)) "
            "WHERE QUERY_ID=%s"
        )
        self.cursor.execute(query, (self.cursor.sfqid,))  # get the last executed query using the query id
        try:
            latest_query = self.cursor.fetchone()[0]
            if not latest_query.lower().startswith("select "):
                raise ValueError("Only select queries are supported for registering featuring sets")
        except IndexError:
            raise ValueError("No query seems to have been executed in this session")
        return latest_query


class DeltaTable(DataSourceWrapper):
    def __init__(self, path, version=-1, timestamp=None, filter=None):
        self.path = path
        self.version = version
        self.timestamp = timestamp
        self.filter = filter
        if version and timestamp:
            raise ValueError("Only one of version or timestamp is supported")

    def get_raw_data_location(self, stub: CoreServiceApi):
        delta_table = V1DeltaTableSpec(
            path=self.path,
            version=self.version
        )
        if self.timestamp:
            delta_table.timestamp = self.timestamp
        if self.filter:
            delta_table.filter = self.filter._filter
        raw_data_location = V1RawDataLocation(
            delta_table=delta_table
        )
        return raw_data_location


class CSVFolder(FileDataSourceWrapper):
    def __init__(self, root_folder, delimiter=",", filter_pattern=""):
        super().__init__(root_folder)
        self.root_folder = root_folder
        self.filter_pattern = filter_pattern
        self.delimiter = delimiter

    def get_raw_data_location(self, stub: CoreServiceApi):
        if self.is_local():
            self._write_to_storage(stub, self.filter_pattern)

        csv_folder = V1CSVFolderSpec(
            root_folder=self.external_path,
            filter_pattern=self.filter_pattern,
            delimiter=self.delimiter
        )
        raw_data_location = V1RawDataLocation(
            csv_folder=csv_folder
        )
        return raw_data_location


class ParquetFolder(FileDataSourceWrapper):
    def __init__(self, root_folder, filter_pattern=""):
        super().__init__(root_folder)
        self.root_folder = root_folder
        self.filter_pattern = filter_pattern

    def get_raw_data_location(self, stub: CoreServiceApi):
        if self.is_local():
            self._write_to_storage(stub, self.filter_pattern)
        raw_data_location = V1RawDataLocation(
            parquet_folder=V1ParquetFolderSpec(
                root_folder=self.external_path,
                filter_pattern=self.filter_pattern
            )
        )
        return raw_data_location


class JSONFolder(FileDataSourceWrapper):
    def __init__(self, root_folder, multiline=False, filter_pattern=""):
        super().__init__(root_folder)
        self.root_folder = root_folder
        self.multiline = multiline
        self.filter_pattern = filter_pattern

    def get_raw_data_location(self, stub: CoreServiceApi):
        if self.is_local():
            self._write_to_storage(stub, self.filter_pattern)
        raw_data_location = V1RawDataLocation(
            json_folder=V1JSONFolderSpec(
                root_folder=self.external_path,
                filter_pattern=self.filter_pattern,
                multiline=self.multiline
            )
        )
        return raw_data_location


class MongoDbCollection(DataSourceWrapper):
    def __init__(self, connection_uri="mongodb://localhost:27017/", database="", collection=""):
        if not database:
            raise ValueError("Database name is required!")
        if not collection:
            raise ValueError("Collection name is required!")
        self.connection_uri = connection_uri
        self.database = database
        self.collection = collection

    def get_raw_data_location(self, stub: CoreServiceApi):
        raw_data_location = V1RawDataLocation(
            mongo_db=V1MongoDbCollectionSpec(
                connection_uri=self.connection_uri,
                database=self.database,
                collection=self.collection,
            )
        )
        return raw_data_location


class BigQueryTable(DataSourceWrapper):
    def __init__(
        self,
        table="",
        parent_project="",
        query="",
        materialization_dataset="",
    ):
        if not (table or query):
            raise ValueError("Table or query is required!")
        if table and query:
            raise ValueError("Only one of table or query is supported!")
        if query and not materialization_dataset:
            raise ValueError("When query is specified, then materialization_dataset is required!")
        self.table = table
        self.parent_project = parent_project
        self.query = query
        self.materialization_dataset = materialization_dataset

    def get_raw_data_location(self, stub: CoreServiceApi):
        raw_data_location = V1RawDataLocation(
            google_big_query=V1BigQueryTableSpec(
                table=self.table,
                parent_project=self.parent_project,
                query=self.query,
                materialization_dataset = self.materialization_dataset,
            )
        )
        return raw_data_location


def get_source(raw_data_location: V1RawDataLocation):
    if raw_data_location.get("csv"):
        csv = raw_data_location.csv
        return CSVFile(path=csv.path, delimiter=csv.delimiter)
    elif raw_data_location.get("json"):
        json = raw_data_location.json
        return JSONFile(path=json.path, multiline=json.multiline)
    elif raw_data_location.get("parquet"):
        parquet = raw_data_location.parquet
        return ParquetFile(path=parquet.path)
    elif raw_data_location.get("snowflake"):
        snowflake = raw_data_location.snowflake
        proxy = (
            Proxy(
                host=snowflake.proxy.host,
                port=snowflake.proxy.port,
                user=snowflake.proxy.user,
                password=snowflake.proxy.password,
            )
            if snowflake.get("proxy")
            else None
        )

        return SnowflakeTable(
            table=snowflake.table,
            database=snowflake.database,
            url=snowflake.url,
            warehouse=snowflake.warehouse,
            schema=snowflake.schema,
            query=snowflake.query,
            insecure=snowflake.insecure,
            role=snowflake.role,
            account=snowflake.account,
            proxy=proxy,
        )
    elif raw_data_location.get("jdbc"):
        jdbc = raw_data_location.jdbc
        partition_options = PartitionOptions(
            num_partitions=jdbc.num_partitions,
            partition_column=jdbc.partition_column,
            lower_bound=jdbc.lower_bound,
            upper_bound=jdbc.upper_bound,
            fetch_size=jdbc.fetch_size,
        )
        return JdbcTable(
            connection_url=jdbc.connection_url, table=jdbc.table, query=jdbc.query, partition_options=partition_options
        )
    elif raw_data_location.get("delta_table"):
        delta_table = raw_data_location.delta_table
        filter = delta_table.filter if (delta_table.get("filter")) else None
        return DeltaTable(
            path=delta_table.path, version=delta_table.version, timestamp=delta_table.timestamp, filter=filter
        )
    elif raw_data_location.get("csv_folder"):
        csv_folder = raw_data_location.csv_folder
        return CSVFolder(
            root_folder=csv_folder.root_folder, filter_pattern=csv_folder.filter_pattern, delimiter=csv_folder.delimiter
        )
    elif raw_data_location.get("parquet_folder"):
        parquet_folder = raw_data_location.parquet_folder
        return ParquetFolder(root_folder=parquet_folder.root_folder, filter_pattern=parquet_folder.filter_pattern)
    elif raw_data_location.get("json_folder"):
        json_folder = raw_data_location.json_folder
        return JSONFolder(
            root_folder=json_folder.root_folder,
            filter_pattern=json_folder.filter_pattern,
            multiline=json_folder.multiline,
        )
    elif raw_data_location.get("mongo_db"):
        mongo_db = raw_data_location.mongo_db
        return MongoDbCollection(
            connection_uri=mongo_db.connection_uri, database=mongo_db.database, collection=mongo_db.collection
        )
    elif raw_data_location.get("big_query"):
        big_query = raw_data_location.big_query
        return BigQueryTable(
            table=big_query.table,
            parent_project=big_query.parent_project,
            query=big_query.query,
            materialization_dataset=big_query.materialization_dataset,
        )
    else:
        raise Exception("Unsupported external data source.")
