#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import datetime
import decimal
import os
import tempfile
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, as_completed, wait
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import jaydebeapi
import pytz
from _decimal import ROUND_HALF_EVEN, ROUND_HALF_UP
from dateutil import parser

import snowflake.snowpark
from snowflake.connector.options import pandas as pd
from snowflake.snowpark import DataFrameReader
from snowflake.snowpark._internal.utils import (
    TempObjectType,
    get_temp_type_for_object,
    normalize_local_file,
    random_name_for_temp_object,
)
from snowflake.snowpark.dataframe import DataFrame
from snowflake.snowpark.types import (
    BinaryType,
    DataType,
    DateType,
    DecimalType,
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
    TimeType,
    _NumericType,
)
from snowflake.snowpark_connect.error.error_codes import ErrorCodes
from snowflake.snowpark_connect.error.error_utils import attach_custom_error_code
from snowflake.snowpark_connect.relation.read.utils import (
    DATA_SOURCE_SQL_COMMENT,
    Connection,
    exponential_backoff,
)
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger


class JdbcDialect:
    """
    Base class for datasource dialect.
    It defines default behavior for any unsupported datasource dialect.
    """

    def __init__(self, datasource_name: str) -> None:
        self.datasource_name = datasource_name

    def can_handle(self, url: str) -> bool:
        """
        Can this dialect handle the provided JDBC URL?
        :param url: JDBC URL
        :return: Always True as this is register last and provide default JDBC functionality.
        """
        return True

    def get_max_varchar_length(self) -> int:
        """
        Get the maximum size of the VARCHAR datatype supported.
        :return: max varchar size
        """
        return 16 * 1024 * 1024

    def get_double_type_name(self) -> str:
        """
        Get the DOUBLE type string name. SQL Server support it as REAL.
        :return: String name of DOUBLE datatype
        """
        return "DOUBLE"

    def support_numeric_in_quote(self) -> bool:
        """
        Does JDBC datasource support numeric in quote. e.g. where id > '5'
        :return: True if it supports otherwise False
        """
        return True


# We will derive it from DataFrameReader of Snowpark once they merge and we refactor
# the code to reuse as much from Snowpark.
class JdbcDataFrameReader(DataFrameReader):
    """
    Derived Snowflake DataFrameReader class, so we cna reuse methods.
    This class read data from a JDBC datasource and creates Snowpark Dataframe.
    """

    def __init__(
        self,
        session: "snowflake.snowpark.session.Session",
        jdbc_options: dict[str, str],
    ) -> None:
        super().__init__(session)
        self.session = session
        self.jdbc_options = jdbc_options
        register_all_supported_jdbc_dialect()

    def jdbc_read_dbapi(
        self,
        create_connection: Callable[[dict[str, str]], "Connection"],
        close_connection: Callable[[Connection], None],
        table: Optional[str] = None,
        query: Optional[str] = None,
        *,
        column: Optional[str] = None,
        lower_bound: Optional[Union[str, int]] = None,
        upper_bound: Optional[Union[str, int]] = None,
        num_partitions: Optional[int] = None,
        max_workers: Optional[int] = None,
        query_timeout: Optional[int] = 0,
        predicates: Optional[List[str]] = None,
    ) -> DataFrame:

        """
        Read a table from JDBC datasource.
        If user provided column info then read in parallel using threadpool.

        Read rows using query provided. Execute this query against the JDBC Datasource to get rows.
        table name and query are mutually execlusive options. Both can't be used at the same time.
        Query option won't read in parallel as column parameters won't allowed.
        If column is specified then predicates will be ignored
        """
        url = self.jdbc_options.get("url", None)
        jdbc_dialect = get_jdbc_dialect(url)
        conn = None
        try:
            conn = create_connection(self.jdbc_options)

            # this is specified to pyodbc, need other way to manage timeout on other drivers
            conn.timeout = query_timeout

            struct_schema, raw_schema = self._infer_data_source_schema(
                conn, table, query
            )

            if column is None:
                if (
                    lower_bound is not None
                    or upper_bound is not None
                    or num_partitions is not None
                ):
                    exception = ValueError(
                        "when column is not specified, lower_bound, upper_bound, num_partitions are expected to be None"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_INPUT)
                    raise exception
                if table is not None:
                    partitioned_queries = []
                    table_query = f"SELECT * FROM {table}"
                    if predicates is not None and len(predicates) > 0:
                        where_clause = " AND ".join(predicates)
                        table_query += f" WHERE {where_clause}"
                    partitioned_queries.append(table_query)
                elif query is not None:
                    partitioned_queries = [query]
                else:
                    exception = ValueError("table or query is not specified")
                    attach_custom_error_code(exception, ErrorCodes.INSUFFICIENT_INPUT)
                    raise exception
            else:
                if lower_bound is None or upper_bound is None or num_partitions is None:
                    exception = ValueError(
                        "when column is specified, lower_bound, upper_bound, num_partitions must be specified"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_INPUT)
                    raise exception

                column_type = None
                for field in struct_schema.fields:
                    if field.name.lower() == column.lower():
                        column_type = field.datatype
                if column_type is None:
                    exception = ValueError("Column does not exist")
                    attach_custom_error_code(exception, ErrorCodes.COLUMN_NOT_FOUND)
                    raise exception

                if not isinstance(column_type, _NumericType) and not isinstance(
                    column_type, DateType
                ):
                    exception = ValueError(f"unsupported type {column_type}")
                    attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
                    raise exception
                spark_column_name = f'"{column}"'
                partitioned_queries = self._generate_partition(
                    table,
                    column_type,
                    jdbc_dialect,
                    spark_column_name,
                    lower_bound,
                    upper_bound,
                    num_partitions,
                )
            with tempfile.TemporaryDirectory() as tmp_dir:
                # TODO: Creating temp table and temp stage can be done in parallel, and
                # could be done earlier.

                # create temp table
                snowflake_table_type = "temporary"
                snowflake_table_name = random_name_for_temp_object(TempObjectType.TABLE)
                self.session.create_dataframe(
                    data=[], schema=struct_schema
                ).write.save_as_table(
                    snowflake_table_name, table_type=snowflake_table_type
                )
                res_df = self.table(snowflake_table_name)

                # create temp stage
                snowflake_stage_name = random_name_for_temp_object(TempObjectType.STAGE)
                sql_create_temp_stage = f"create {get_temp_type_for_object(self.session._use_scoped_temp_objects, True)} stage if not exists {snowflake_stage_name}"
                self.session._run_query(
                    sql_create_temp_stage, is_ddl_on_temp_object=True
                )

                # TODO: Set max workers depending on local resources
                # TODO: Use a thread pool executor that uses ordered or priority queue.
                # It is likely (but not guaranteed) that the first partitions have more rows
                # than later partitions.
                with ThreadPoolExecutor(
                    max_workers=max_workers
                ) as query_thread_executor, ThreadPoolExecutor(
                    max_workers=max_workers
                ) as upload_thread_executor:
                    upload_thread_pool_futures = []
                    query_thread_pool_futures = [
                        query_thread_executor.submit(
                            _task_fetch_from_data_source,
                            create_connection,
                            self.jdbc_options,
                            close_connection,
                            query,
                            raw_schema,
                            i,
                            tmp_dir,
                            query_timeout,
                        )
                        for i, query in enumerate(partitioned_queries)
                    ]
                    for future in as_completed(query_thread_pool_futures):
                        if isinstance(future.result(), Exception):
                            logger.debug(
                                "fetch from data source failed, canceling all running tasks"
                            )
                            query_thread_executor.shutdown(wait=False)
                            upload_thread_executor.shutdown(wait=False)
                            exception = future.result()
                            attach_custom_error_code(
                                exception, ErrorCodes.INTERNAL_ERROR
                            )
                            raise exception
                        else:
                            path = future.result()
                            if not path:
                                logger.error("We can skip the empty path")
                                continue

                            upload_thread_pool_futures.append(
                                upload_thread_executor.submit(
                                    self._upload_and_copy_into_table,
                                    path,
                                    snowflake_stage_name,
                                    snowflake_table_name,
                                    "abort_statement",
                                )
                            )
                    completed_futures = wait(
                        upload_thread_pool_futures, return_when=ALL_COMPLETED
                    )
                    for f in completed_futures.done:
                        if f.result() is not None and isinstance(f.result(), Exception):
                            logger.debug(
                                "upload and copy into table failed, canceling all running tasks"
                            )
                            query_thread_executor.shutdown(wait=False)
                            upload_thread_executor.shutdown(wait=False)
                            exception = f.result()
                            attach_custom_error_code(
                                exception, ErrorCodes.INTERNAL_ERROR
                            )
                            raise exception
        finally:
            close_connection(conn)

        return res_df

    def _infer_data_source_schema(
        self,
        conn: Connection,
        table: Optional[str] = None,
        query: Optional[str] = None,
    ) -> tuple[StructType, tuple[tuple[str, Any, int, int, int, int, bool]]]:
        if table is not None:
            sql = f"SELECT * FROM {table} WHERE 1=0"
        elif query is not None:
            sql = f"SELECT * FROM ({query}) WHERE 1=0"
        else:
            exception = ValueError("table or query is not specified")
            attach_custom_error_code(exception, ErrorCodes.INSUFFICIENT_INPUT)
            raise exception

        cursor = conn.cursor()
        cursor.execute(sql)
        raw_schema = cursor.description
        rc = self._to_snowpark_type(raw_schema), raw_schema
        cursor.close()
        return rc

    # this function is only used in data source API for SQL server
    def _to_internal_value(self, value: Union[int, str, float], column_type: DataType):
        if isinstance(column_type, _NumericType):
            return int(value)
        elif isinstance(column_type, (TimestampType, DateType)):
            # TODO: SNOW-1909315: support timezone
            dt = parser.parse(value)
            return int(dt.replace(tzinfo=pytz.UTC).timestamp())
        else:
            exception = TypeError(
                f"unsupported column type for partition: {column_type}"
            )
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
            raise exception

    # this function is only used in data source API for SQL server
    def _to_external_value(self, value: Union[int, str, float], column_type: DataType):
        if isinstance(column_type, _NumericType):
            return value
        elif isinstance(column_type, (TimestampType, DateType)):
            # TODO: SNOW-1909315: support timezone
            return datetime.datetime.fromtimestamp(value, tz=pytz.UTC)
        else:
            exception = TypeError(
                f"unsupported column type for partition: {column_type}"
            )
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
            raise exception

    def _to_snowpark_type(self, schema: Tuple[tuple]) -> StructType:
        fields = []
        for column in schema:
            name, dbapi_type, size, _, precision, scale, is_nullable = column
            match dbapi_type:
                case jaydebeapi.NUMBER:
                    field = StructField(name, IntegerType(), is_nullable)
                case jaydebeapi.FLOAT:
                    field = StructField(name, FloatType(), is_nullable)
                case jaydebeapi.DECIMAL:
                    field = StructField(
                        name,
                        DecimalType(int(precision), int(scale)),
                        is_nullable,
                    )
                case jaydebeapi.STRING:
                    field = StructField(name, StringType(), is_nullable)
                case jaydebeapi.DATE:
                    field = StructField(name, DateType(), is_nullable)
                case jaydebeapi.TIME:
                    field = StructField(name, TimeType(), is_nullable)
                case jaydebeapi.DATETIME:
                    field = StructField(name, TimestampType(), is_nullable)
                case jaydebeapi.BINARY:
                    field = StructField(name, BinaryType(), is_nullable)
                case _:
                    exception = ValueError(f"unsupported type: {dbapi_type}")
                    attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
                    raise exception

            fields.append(field)
        return StructType(fields)

    def _generate_partition(
        self,
        table: str,
        column_type: DataType,
        jdbc_dialect: JdbcDialect,
        column: Optional[str] = None,
        lower_bound: Optional[Union[str, int]] = None,
        upper_bound: Optional[Union[str, int]] = None,
        num_partitions: Optional[int] = None,
    ) -> List[str]:
        select_query = f"SELECT * FROM {table}"

        processed_lower_bound = self._to_internal_value(lower_bound, column_type)
        processed_upper_bound = self._to_internal_value(upper_bound, column_type)
        if processed_lower_bound > processed_upper_bound:
            exception = ValueError("lower_bound cannot be greater than upper_bound")
            attach_custom_error_code(exception, ErrorCodes.INVALID_INPUT)
            raise exception

        if processed_lower_bound == processed_upper_bound or num_partitions <= 1:
            return [select_query]

        if (processed_upper_bound - processed_lower_bound) >= num_partitions or (
            processed_upper_bound - processed_lower_bound
        ) < 0:
            actual_num_partitions = num_partitions
        else:
            actual_num_partitions = processed_upper_bound - processed_lower_bound
            logger.warning(
                "The number of partitions is reduced because the specified number of partitions is less than the difference between upper bound and lower bound."
            )

        # decide stride length
        upper_stride = (
            processed_upper_bound / decimal.Decimal(actual_num_partitions)
        ).quantize(decimal.Decimal("1e-18"), rounding=ROUND_HALF_EVEN)
        lower_stride = (
            processed_lower_bound / decimal.Decimal(actual_num_partitions)
        ).quantize(decimal.Decimal("1e-18"), rounding=ROUND_HALF_EVEN)
        preciseStride = upper_stride - lower_stride
        stride = int(preciseStride)

        lost_num_of_strides = (
            (preciseStride - decimal.Decimal(stride))
            * decimal.Decimal(actual_num_partitions)
            / decimal.Decimal(stride)
        )
        lower_bound_with_stride_alignment = processed_lower_bound + int(
            (lost_num_of_strides / 2 * decimal.Decimal(stride)).quantize(
                decimal.Decimal("1"), rounding=ROUND_HALF_UP
            )
        )

        current_value = lower_bound_with_stride_alignment
        numeric_in_quote = jdbc_dialect.support_numeric_in_quote()
        if isinstance(column_type, _NumericType) and not numeric_in_quote:
            single_quote = ""
        else:
            single_quote = "'"

        partition_queries = []
        for i in range(actual_num_partitions):
            l_bound = (
                f"{column} >= {single_quote}{self._to_external_value(current_value, column_type)}{single_quote}"
                if i != 0
                else ""
            )
            current_value += stride
            u_bound = (
                f"{column} < {single_quote}{self._to_external_value(current_value, column_type)}{single_quote}"
                if i != actual_num_partitions - 1
                else ""
            )

            if u_bound == "":
                where_clause = l_bound
            elif l_bound == "":
                where_clause = f"{u_bound} OR {column} is null"
            else:
                where_clause = f"{l_bound} AND {u_bound}"

            partition_queries.append(select_query + f" WHERE {where_clause}")

        return partition_queries

    @exponential_backoff
    def _upload_and_copy_into_table(
        self,
        local_file: str,
        snowflake_stage_name: str,
        snowflake_table_name: Optional[str] = None,
        on_error: Optional[str] = "abort_statement",
        statements_params: Optional[Dict[str, str]] = None,
    ):
        file_name = os.path.basename(local_file)
        self._session.file.put(
            normalize_local_file(local_file),
            f"{snowflake_stage_name}",
            overwrite=True,
            statement_params=statements_params,
        )

        copy_into_table_query = f"""
        COPY INTO {snowflake_table_name} FROM @{snowflake_stage_name}/{file_name}
        FILE_FORMAT = (TYPE = PARQUET USE_VECTORIZED_SCANNER=TRUE)
        MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE
        PURGE=TRUE
        ON_ERROR={on_error}
        {DATA_SOURCE_SQL_COMMENT}
        """
        self._session.sql(copy_into_table_query).collect(
            statement_params=statements_params
        )


@exponential_backoff
def _task_fetch_from_data_source(
    create_connection: Callable[[dict[str, str]], "Connection"],
    jdbc_options: dict[str, str],
    close_connection: Callable[[Connection], None],
    query: str,
    schema: tuple[tuple[str, Any, int, int, int, int, bool]],
    partitioned_query_index: int,
    tmp_dir: str,
    query_timeout: int = 0,
) -> str:
    conn = None
    try:
        # TODO: This should use connection pooling.
        conn = create_connection(jdbc_options)
        # this is specified to pyodbc, need other way to manage timeout on other drivers
        conn.timeout = query_timeout
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        # We will only go through with writing an empty file for the first partition.
        # Otherwise, we will return an empty path to indicate there is no data.
        if not result and partitioned_query_index != 0:
            logger.info(f"Query gave no results {query}")
            cursor.close()
            return ""

        columns = [col[0] for col in schema]
        df = pd.DataFrame.from_records(result, columns=columns)
        path = os.path.join(tmp_dir, f"data_{partitioned_query_index}.parquet")
        df.to_parquet(path)
        cursor.close()
    finally:
        close_connection(conn)
    return path


# Hold all registered JDBC Dialects
jdbc_dialects: List["JdbcDialect"] = []


class SnowflakeJdbcDialect(JdbcDialect):
    """
    For internal testing uses Snowflake JDBC Driver.
    Defines Snowflake capability.
    """

    def can_handle(self, url: str) -> bool:
        """
        Can this dialect handle the provided JDBC URL?
        :param url: JDBC URL
        :return: True if URL is for Snowflake JDBC driver otherwise False.
        """
        return url.lower().startswith("jdbc:snowflake:")

    def get_max_varchar_length(self) -> int:
        """
        Get the maximum size of the VARCHAR datatype supported.
        :return: max varchar size
        """
        return 16 * 1024 * 1024

    def get_double_type_name(self) -> str:
        """
        Get the DOUBLE type string name.
        :return: String name of DOUBLE datatype
        """
        return "DOUBLE"


class SqlserverJdbcDialect(JdbcDialect):
    """
    Defines SQL Server specific capability.
    """

    def can_handle(self, url: str) -> bool:
        """
        Can this dialect handle the provided JDBC URL?
        :param url: JDBC URL
        :return: True if URL is for SQL Server JDBC driver otherwise False.
        """
        return url.lower().startswith("jdbc:sqlserver:")

    def get_max_varchar_length(self) -> int:
        """
        Get the maximum size of the VARCHAR datatype supported.
        :return: max varchar size
        """
        return 8000

    def get_double_type_name(self) -> str:
        """
        Get the DOUBLE type string name.
        :return: String name of DOUBLE datatype
        """
        return "REAL"


class DerbyJdbcDialect(JdbcDialect):
    """
    Defines Derby specific capability.
    Derby is used by Spark Datasource tests
    """

    def can_handle(self, url: str) -> bool:
        """
        Can this dialect handle the provided JDBC URL?
        :param url: JDBC URL
        :return: True if URL is for SQL Server JDBC driver otherwise False.
        """
        return url.lower().startswith("jdbc:derby:")

    def support_numeric_in_quote(self) -> bool:
        """
        Does JDBC datasource support numeric in quote. e.g. where id > '5'
        :return: True if it supports otherwise False
        """
        return False


class PostgresqlJdbcDialect(JdbcDialect):
    """
    Defines Postgresql specific capability.
    """

    def can_handle(self, url: str) -> bool:
        """
        Can this dialect handle the provided JDBC URL?
        :param url: JDBC URL
        :return: True if URL is for Postgresql JDBC driver otherwise False.
        """
        return url.lower().startswith("jdbc:postgresql:")

    def get_max_varchar_length(self) -> int:
        """
        Get the maximum size of the VARCHAR datatype supported.
        :return: max varchar size
        """
        return 10485760

    def get_double_type_name(self) -> str:
        """
        Get the DOUBLE type string name.
        :return: String name of DOUBLE datatype
        """
        return "DOUBLE PRECISION"


class MySqlJdbcDialect(JdbcDialect):
    """
    Defines MySQL specific capability.
    """

    def can_handle(self, url: str) -> bool:
        """
        Can this dialect handle the provided JDBC URL?
        :param url: JDBC URL
        :return: True if URL is for MySQL JDBC driver otherwise False.
        """
        return url.lower().startswith("jdbc:mysql:")

    def get_max_varchar_length(self) -> int:
        """
        Get the maximum size of the VARCHAR datatype supported.
        :return: max varchar size
        """
        return 4000

    def get_double_type_name(self) -> str:
        """
        Get the DOUBLE type string name.
        :return: String name of DOUBLE datatype
        """
        return "DOUBLE"


def register_jdbc_dialect(dialect) -> None:
    """
    Register  a supported JDBC datasource
    :param dialect: Dialect class of a JDBC datasource
    """
    jdbc_dialects.append(dialect)


def register_all_supported_jdbc_dialect() -> None:
    """
    Register all supported JDBC datasources
    """
    if len(jdbc_dialects) == 0:
        register_jdbc_dialect(DerbyJdbcDialect("derby"))
        register_jdbc_dialect(MySqlJdbcDialect("mysql"))
        register_jdbc_dialect(PostgresqlJdbcDialect("postgresql"))
        register_jdbc_dialect(SnowflakeJdbcDialect("snowflake"))
        register_jdbc_dialect(SqlserverJdbcDialect("sqlserver"))
        # Register this at last
        register_jdbc_dialect(JdbcDialect("default"))


def get_jdbc_dialect(url: str) -> JdbcDialect:
    """
    Get the JDBc Dialect class from the given JDBC URL
    :param url: JDBC URL of a driver
    :return: JDBC Dialect class
    """
    for jdbc_dialect in jdbc_dialects:
        if jdbc_dialect.can_handle(url):
            return jdbc_dialect
    exception = ValueError(f"Unsupported JDBC datasource: {url}")
    attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
    raise exception
