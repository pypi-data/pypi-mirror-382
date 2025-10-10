#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import os
import shutil
from pathlib import Path

import pyspark.sql.connect.proto.base_pb2 as proto_base
import pyspark.sql.connect.proto.commands_pb2 as commands_proto
from pyspark.errors.exceptions.base import AnalysisException

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
    unquote_if_quoted,
)
from snowflake.snowpark.exceptions import SnowparkSQLException
from snowflake.snowpark.functions import col, lit, object_construct, sql_expr
from snowflake.snowpark.types import (
    ArrayType,
    DataType,
    DateType,
    MapType,
    StringType,
    StructType,
    TimestampType,
    _NumericType,
)
from snowflake.snowpark_connect.config import (
    auto_uppercase_column_identifiers,
    global_config,
    sessions_config,
    str_to_bool,
)
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.error.error_codes import ErrorCodes
from snowflake.snowpark_connect.error.error_utils import attach_custom_error_code
from snowflake.snowpark_connect.relation.io_utils import (
    convert_file_prefix_path,
    get_compression_for_source_and_options,
    is_cloud_path,
)
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.relation.read.metadata_utils import (
    filter_metadata_columns,
)
from snowflake.snowpark_connect.relation.read.reader_config import CsvWriterConfig
from snowflake.snowpark_connect.relation.stage_locator import get_paths_from_stage
from snowflake.snowpark_connect.relation.utils import (
    generate_spark_compatible_filename,
    random_string,
)
from snowflake.snowpark_connect.type_mapping import snowpark_to_iceberg_type
from snowflake.snowpark_connect.utils.context import get_session_id
from snowflake.snowpark_connect.utils.identifiers import (
    spark_to_sf_single_id,
    split_fully_qualified_spark_name,
)
from snowflake.snowpark_connect.utils.io_utils import get_table_type
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
    telemetry,
)

_column_order_for_write = "name"


# TODO: We will revise/refactor this after changes for all formats are finalized.
def clean_params(params):
    """
    Clean params for write operation. This, for now, allows us to use the same parameter code that
    read operations use.
    """
    # INFER_SCHEMA does not apply to writes
    if "INFER_SCHEMA" in params["format_type_options"]:
        del params["format_type_options"]["INFER_SCHEMA"]


def get_param_from_options(params, options, source):
    match source:
        case "csv":
            config = CsvWriterConfig(options)
            snowpark_args = config.convert_to_snowpark_args()

            if "header" in options:
                params["header"] = str_to_bool(options["header"])
            params["single"] = False

            params["format_type_options"] = snowpark_args
            clean_params(params)
        case "json":
            params["format_type_options"]["FILE_EXTENSION"] = source
        case "parquet":
            params["header"] = True
        case "text":
            config = CsvWriterConfig(options)
            params["format_type_options"]["FILE_EXTENSION"] = "txt"
            params["format_type_options"]["ESCAPE_UNENCLOSED_FIELD"] = "NONE"
            if "lineSep" in options:
                params["format_type_options"]["RECORD_DELIMITER"] = config.get(
                    "linesep"
                )

    if (
        source in ("csv", "parquet", "json") and "nullValue" in options
    ):  # TODO: Null value handling if not specified
        params["format_type_options"]["NULL_IF"] = options["nullValue"]


def _spark_to_snowflake(multipart_id: str) -> str:
    return ".".join(
        spark_to_sf_single_id(part)
        for part in split_fully_qualified_spark_name(multipart_id)
    )


def map_write(request: proto_base.ExecutePlanRequest):
    write_op = request.plan.command.write_operation
    telemetry.report_io_write(write_op.source)

    write_mode = None
    match write_op.mode:
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_APPEND:
            write_mode = "append"
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_ERROR_IF_EXISTS:
            write_mode = "errorifexists"
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_OVERWRITE:
            write_mode = "overwrite"
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_IGNORE:
            write_mode = "ignore"

    result = map_relation(write_op.input)
    input_df: snowpark.DataFrame = handle_column_names(result, write_op.source)

    # Create updated container with transformed dataframe, then filter METADATA$FILENAME columns
    # Update the container to use the transformed dataframe from handle_column_names
    updated_result = DataFrameContainer(
        dataframe=input_df,
        column_map=result.column_map,
        table_name=result.table_name,
        alias=result.alias,
        partition_hint=result.partition_hint,
    )
    updated_result = filter_metadata_columns(updated_result)
    input_df = updated_result.dataframe

    session: snowpark.Session = get_or_create_snowpark_session()

    # Check for partition hint early to determine precedence over single option
    partition_hint = (
        result.partition_hint if hasattr(result, "partition_hint") else None
    )

    # Snowflake saveAsTable doesn't support format
    if (
        write_op.HasField("table")
        and write_op.HasField("source")
        and write_op.source in ("csv", "parquet", "json", "text")
    ):
        write_op.source = ""

    should_write_to_single_file = str_to_bool(write_op.options.get("single", "false"))

    # Support Snowflake-specific snowflake_max_file_size option. This is NOT a spark option.
    max_file_size = None
    if (
        "snowflake_max_file_size" in write_op.options
        and int(write_op.options["snowflake_max_file_size"]) > 0
    ):
        max_file_size = int(write_op.options["snowflake_max_file_size"])
    elif should_write_to_single_file:
        # providing default size as 1GB for single file write
        max_file_size = 1073741824
    match write_op.source:
        case "csv" | "parquet" | "json" | "text":
            write_path = get_paths_from_stage(
                [write_op.path],
                session=session,
            )[0]
            # Generate Spark-compatible filename with proper extension
            extension = write_op.source if write_op.source != "text" else "txt"

            compression = get_compression_for_source_and_options(
                write_op.source, write_op.options, from_read=False
            )
            if compression is not None:
                write_op.options["compression"] = compression

            # Generate Spark-compatible filename or prefix
            # we need a random prefix to support "append" mode
            # otherwise copy into with overwrite=False will fail if the file already exists
            overwrite = (
                write_op.mode
                == commands_proto.WriteOperation.SaveMode.SAVE_MODE_OVERWRITE
            )

            if overwrite:
                try:
                    path_after_stage = (
                        write_path.split("/", 1)[1] if "/" in write_path else ""
                    )
                    if not path_after_stage or path_after_stage == "/":
                        logger.warning(
                            f"Skipping REMOVE for root path {write_path} - too broad scope"
                        )
                    else:
                        remove_command = f"REMOVE '{write_path}/'"
                        session.sql(remove_command).collect()
                        logger.info(f"Successfully cleared directory: {write_path}")
                except Exception as e:
                    logger.warning(f"Could not clear directory {write_path}: {e}")

            if should_write_to_single_file and partition_hint is None:
                # Single file: generate complete filename with extension
                spark_filename = generate_spark_compatible_filename(
                    task_id=0,
                    attempt_number=0,
                    compression=compression,
                    format_ext=extension,
                )
                temp_file_prefix_on_stage = f"{write_path}/{spark_filename}"
            else:
                # Multiple files: generate prefix without extension (Snowflake will add extensions)
                spark_filename_prefix = generate_spark_compatible_filename(
                    task_id=0,
                    attempt_number=0,
                    compression=None,
                    format_ext="",  # No extension for prefix
                )
                temp_file_prefix_on_stage = f"{write_path}/{spark_filename_prefix}"

            parameters = {
                "location": temp_file_prefix_on_stage,
                "file_format_type": write_op.source
                if write_op.source != "text"
                else "csv",
                "format_type_options": {
                    "COMPRESSION": compression,
                },
                "overwrite": overwrite,
            }
            # Download from the base write path to ensure we fetch whatever Snowflake produced.
            # Using the base avoids coupling to exact filenames/prefixes.
            download_stage_path = write_path

            # Apply max_file_size for both single and multi-file scenarios
            # This helps control when Snowflake splits files into multiple parts
            if max_file_size:
                parameters["max_file_size"] = max_file_size
            # Only apply single option if no partition hint is present (partition hint takes precedence)
            if should_write_to_single_file and partition_hint is None:
                parameters["single"] = True
            rewritten_df: snowpark.DataFrame = rewrite_df(input_df, write_op.source)
            get_param_from_options(parameters, write_op.options, write_op.source)
            if write_op.partitioning_columns:
                if write_op.source != "parquet":
                    exception = SnowparkConnectNotImplementedError(
                        "Partitioning is only supported for parquet format"
                    )
                    attach_custom_error_code(
                        exception, ErrorCodes.UNSUPPORTED_OPERATION
                    )
                    raise exception
                # Build Spark-style directory structure: col1=value1/col2=value2/...
                # Example produced expression (Snowflake SQL):
                #   'department=' || TO_VARCHAR("department") || '/' || 'region=' || TO_VARCHAR("region")
                partitioning_column_names = list(write_op.partitioning_columns)
                partition_expr_parts: list[str] = []
                for col_name in partitioning_column_names:
                    quoted = f'"{col_name}"'
                    segment = f"'{col_name}=' || COALESCE(TO_VARCHAR({quoted}), '__HIVE_DEFAULT_PARTITION__')"
                    partition_expr_parts.append(segment)
                parameters["partition_by"] = " || '/' || ".join(partition_expr_parts)
                # When using PARTITION BY, Snowflake writes into subdirectories under the base path.
                # Download from the base write path to preserve partition directories locally.
                download_stage_path = write_path

            # If a partition hint is present (from DataFrame.repartition(n)), optionally split the
            # write into n COPY INTO calls by assigning a synthetic partition id. Controlled by config.
            # Note: This affects only the number of output files, not computation semantics.
            # Partition hints take precedence over single option (matches Spark behavior) when enabled.
            repartition_for_writes_enabled = (
                global_config.snowflake_repartition_for_writes
            )
            if repartition_for_writes_enabled and partition_hint and partition_hint > 0:
                # Create a stable synthetic file number per row using ROW_NUMBER() over a
                # randomized order, then modulo partition_hint. We rely on sql_expr to avoid
                # adding new helpers.
                file_num_col = "_sas_file_num"
                partitioned_df = rewritten_df.withColumn(
                    file_num_col,
                    sql_expr(
                        f"(ROW_NUMBER() OVER (ORDER BY RANDOM())) % {partition_hint}"
                    ),
                )

                # Execute multiple COPY INTO operations, one per target file.
                # Since we write per-partition with distinct prefixes, download from the base write path.
                download_stage_path = write_path
                for part_idx in range(partition_hint):
                    part_params = dict(parameters)
                    # Preserve Spark-like filename prefix per partition so downloaded basenames
                    # match the expected Spark pattern (with possible Snowflake counters appended).
                    per_part_prefix = generate_spark_compatible_filename(
                        task_id=part_idx,
                        attempt_number=0,
                        compression=None,
                        format_ext="",  # prefix only; Snowflake appends extension/counters
                    )
                    part_params["location"] = f"{write_path}/{per_part_prefix}"
                    (
                        partitioned_df.filter(col(file_num_col) == lit(part_idx))
                        .drop(file_num_col)
                        .write.copy_into_location(**part_params)
                    )
            else:
                rewritten_df.write.copy_into_location(**parameters)
            if not is_cloud_path(write_op.path):
                store_files_locally(
                    download_stage_path,
                    write_op.path,
                    overwrite,
                    session,
                )
        case "jdbc":
            from snowflake.snowpark_connect.relation.write.map_write_jdbc import (
                map_write_jdbc,
            )

            options = dict(write_op.options)
            if write_mode is None:
                write_mode = "errorifexists"
            map_write_jdbc(result, session, options, write_mode)
        case "iceberg":
            table_name = (
                write_op.path
                if write_op.path is not None and write_op.path != ""
                else write_op.table.table_name
            )
            snowpark_table_name = _spark_to_snowflake(table_name)

            match write_mode:
                case None | "error" | "errorifexists":
                    table_schema_or_error = _get_table_schema_or_error(
                        snowpark_table_name, session
                    )
                    if isinstance(table_schema_or_error, DataType):  # Table exists
                        exception = AnalysisException(
                            f"Table {snowpark_table_name} already exists"
                        )
                        attach_custom_error_code(
                            exception, ErrorCodes.INVALID_OPERATION
                        )
                        raise exception
                    create_iceberg_table(
                        snowpark_table_name=snowpark_table_name,
                        location=write_op.options.get("location", None),
                        schema=input_df.schema,
                        snowpark_session=session,
                    )
                    _validate_schema_and_get_writer(
                        input_df, "append", snowpark_table_name, table_schema_or_error
                    ).saveAsTable(
                        table_name=snowpark_table_name,
                        mode="append",
                        column_order=_column_order_for_write,
                    )
                case "append":
                    table_schema_or_error = _get_table_schema_or_error(
                        snowpark_table_name, session
                    )
                    if isinstance(table_schema_or_error, DataType):  # Table exists
                        if get_table_type(snowpark_table_name, session) not in (
                            "ICEBERG",
                            "TABLE",
                        ):
                            exception = AnalysisException(
                                f"Table {snowpark_table_name} is not an iceberg table"
                            )
                            attach_custom_error_code(
                                exception, ErrorCodes.INVALID_OPERATION
                            )
                            raise exception
                    else:
                        create_iceberg_table(
                            snowpark_table_name=snowpark_table_name,
                            location=write_op.options.get("location", None),
                            schema=input_df.schema,
                            snowpark_session=session,
                        )
                    _validate_schema_and_get_writer(
                        input_df, "append", snowpark_table_name, table_schema_or_error
                    ).saveAsTable(
                        table_name=snowpark_table_name,
                        mode="append",
                        column_order=_column_order_for_write,
                    )
                case "ignore":
                    table_schema_or_error = _get_table_schema_or_error(
                        snowpark_table_name, session
                    )
                    if not isinstance(
                        table_schema_or_error, DataType
                    ):  # Table not exists
                        create_iceberg_table(
                            snowpark_table_name=snowpark_table_name,
                            location=write_op.options.get("location", None),
                            schema=input_df.schema,
                            snowpark_session=session,
                        )
                        _validate_schema_and_get_writer(
                            input_df, "append", snowpark_table_name
                        ).saveAsTable(
                            table_name=snowpark_table_name,
                            mode="append",
                            column_order=_column_order_for_write,
                        )
                case "overwrite":
                    table_schema_or_error = _get_table_schema_or_error(
                        snowpark_table_name, session
                    )
                    if isinstance(table_schema_or_error, DataType):  # Table exists
                        if get_table_type(snowpark_table_name, session) not in (
                            "ICEBERG",
                            "TABLE",
                        ):
                            exception = AnalysisException(
                                f"Table {snowpark_table_name} is not an iceberg table"
                            )
                            attach_custom_error_code(
                                exception, ErrorCodes.INVALID_OPERATION
                            )
                            raise exception
                    else:
                        create_iceberg_table(
                            snowpark_table_name=snowpark_table_name,
                            location=write_op.options.get("location", None),
                            schema=input_df.schema,
                            snowpark_session=session,
                        )
                    _validate_schema_and_get_writer(
                        input_df, "truncate", snowpark_table_name, table_schema_or_error
                    ).saveAsTable(
                        table_name=snowpark_table_name,
                        mode="truncate",
                        column_order=_column_order_for_write,
                    )
                case _:
                    exception = SnowparkConnectNotImplementedError(
                        f"Write mode {write_mode} is not supported"
                    )
                    attach_custom_error_code(
                        exception, ErrorCodes.UNSUPPORTED_OPERATION
                    )
                    raise exception
        case _:
            snowpark_table_name = _spark_to_snowflake(write_op.table.table_name)
            save_method = write_op.table.save_method

            if (
                write_op.source == "snowflake"
                and write_op.table.save_method
                == commands_proto.WriteOperation.SaveTable.TableSaveMethod.TABLE_SAVE_METHOD_UNSPECIFIED
            ):
                save_method = (
                    commands_proto.WriteOperation.SaveTable.TableSaveMethod.TABLE_SAVE_METHOD_SAVE_AS_TABLE
                )
                if len(write_op.table.table_name) == 0:
                    dbtable_name = write_op.options.get("dbtable", "")
                    if len(dbtable_name) == 0:
                        exception = SnowparkConnectNotImplementedError(
                            "Save command is not supported without a table name"
                        )
                        attach_custom_error_code(
                            exception, ErrorCodes.UNSUPPORTED_OPERATION
                        )
                        raise exception
                    else:
                        snowpark_table_name = _spark_to_snowflake(dbtable_name)

            if (
                save_method
                == commands_proto.WriteOperation.SaveTable.TableSaveMethod.TABLE_SAVE_METHOD_SAVE_AS_TABLE
            ):
                match write_mode:
                    case "overwrite":
                        table_schema_or_error = _get_table_schema_or_error(
                            snowpark_table_name, session
                        )
                        if isinstance(table_schema_or_error, DataType):  # Table exists
                            if get_table_type(snowpark_table_name, session) not in (
                                "NORMAL",
                                "TABLE",
                            ):
                                exception = AnalysisException(
                                    f"Table {snowpark_table_name} is not a FDN table"
                                )
                                attach_custom_error_code(
                                    exception, ErrorCodes.INVALID_OPERATION
                                )
                                raise exception
                            write_mode = "truncate"
                        _validate_schema_and_get_writer(
                            input_df,
                            write_mode,
                            snowpark_table_name,
                            table_schema_or_error,
                        ).saveAsTable(
                            table_name=snowpark_table_name,
                            mode=write_mode,
                            column_order=_column_order_for_write,
                        )
                    case "append":
                        table_schema_or_error = _get_table_schema_or_error(
                            snowpark_table_name, session
                        )
                        if isinstance(
                            table_schema_or_error, DataType
                        ) and get_table_type(  # Table exists
                            snowpark_table_name, session
                        ) not in (
                            "NORMAL",
                            "TABLE",
                        ):
                            exception = AnalysisException(
                                f"Table {snowpark_table_name} is not a FDN table"
                            )
                            attach_custom_error_code(
                                exception, ErrorCodes.INVALID_OPERATION
                            )
                            raise exception

                        _validate_schema_and_get_writer(
                            input_df,
                            write_mode,
                            snowpark_table_name,
                            table_schema_or_error,
                        ).saveAsTable(
                            table_name=snowpark_table_name,
                            mode=write_mode,
                            column_order=_column_order_for_write,
                        )
                    case _:
                        _validate_schema_and_get_writer(
                            input_df, write_mode, snowpark_table_name
                        ).saveAsTable(
                            table_name=snowpark_table_name,
                            mode=write_mode,
                            column_order=_column_order_for_write,
                        )
            elif (
                save_method
                == commands_proto.WriteOperation.SaveTable.TableSaveMethod.TABLE_SAVE_METHOD_INSERT_INTO
            ):
                _validate_schema_and_get_writer(
                    input_df, write_mode, snowpark_table_name
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode=write_mode or "append",
                    column_order=_column_order_for_write,
                )
            else:
                exception = SnowparkConnectNotImplementedError(
                    f"Save command not supported: {save_method}"
                )
                attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
                raise exception


def map_write_v2(request: proto_base.ExecutePlanRequest):
    write_op = request.plan.command.write_operation_v2

    snowpark_table_name = _spark_to_snowflake(write_op.table_name)
    result = map_relation(write_op.input)
    input_df: snowpark.DataFrame = handle_column_names(result, "table")

    # Create updated container with transformed dataframe, then filter METADATA$FILENAME columns
    # Update the container to use the transformed dataframe from handle_column_names
    updated_result = DataFrameContainer(
        dataframe=input_df,
        column_map=result.column_map,
        table_name=result.table_name,
        alias=result.alias,
        partition_hint=result.partition_hint,
    )
    updated_result = filter_metadata_columns(updated_result)
    input_df = updated_result.dataframe

    session: snowpark.Session = get_or_create_snowpark_session()

    if write_op.table_name is None or write_op.table_name == "":
        exception = SnowparkConnectNotImplementedError(
            "Write operation V2 only support table writing now"
        )
        attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
        raise exception

    if write_op.provider.lower() == "iceberg":
        match write_op.mode:
            case commands_proto.WriteOperationV2.MODE_CREATE:
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if isinstance(table_schema_or_error, DataType):  # Table exists
                    exception = AnalysisException(
                        f"Table {snowpark_table_name} already exists"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                    raise exception
                create_iceberg_table(
                    snowpark_table_name=snowpark_table_name,
                    location=write_op.table_properties.get("location"),
                    schema=input_df.schema,
                    snowpark_session=session,
                )
                _validate_schema_and_get_writer(
                    input_df, "append", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="append",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_APPEND:
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if not isinstance(table_schema_or_error, DataType):  # Table not exists
                    exception = AnalysisException(
                        f"[TABLE_OR_VIEW_NOT_FOUND] The table or view `{write_op.table_name}` cannot be found."
                    )
                    attach_custom_error_code(exception, ErrorCodes.INTERNAL_ERROR)
                    raise exception
                if get_table_type(snowpark_table_name, session) not in (
                    "ICEBERG",
                    "TABLE",
                ):
                    exception = AnalysisException(
                        f"Table {snowpark_table_name} is not an iceberg table"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                    raise exception
                _validate_schema_and_get_writer(
                    input_df, "append", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="append",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_OVERWRITE | commands_proto.WriteOperationV2.MODE_OVERWRITE_PARTITIONS:
                # TODO: handle the filter condition for MODE_OVERWRITE
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if isinstance(table_schema_or_error, DataType):  # Table exists
                    if get_table_type(snowpark_table_name, session) not in (
                        "ICEBERG",
                        "TABLE",
                    ):
                        exception = AnalysisException(
                            f"Table {snowpark_table_name} is not an iceberg table"
                        )
                        attach_custom_error_code(
                            exception, ErrorCodes.INVALID_OPERATION
                        )
                        raise exception
                else:
                    exception = AnalysisException(
                        f"[TABLE_OR_VIEW_NOT_FOUND] Table {snowpark_table_name} does not exist"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                    raise exception
                _validate_schema_and_get_writer(
                    input_df, "truncate", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="truncate",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_REPLACE:
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if isinstance(table_schema_or_error, DataType):  # Table exists
                    create_iceberg_table(
                        snowpark_table_name=snowpark_table_name,
                        location=write_op.table_properties.get("location"),
                        schema=input_df.schema,
                        snowpark_session=session,
                        mode="replace",
                    )
                else:
                    exception = AnalysisException(
                        f"Table {snowpark_table_name} does not exist"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                    raise exception
                _validate_schema_and_get_writer(
                    input_df, "replace", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="append",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_CREATE_OR_REPLACE:
                create_iceberg_table(
                    snowpark_table_name=snowpark_table_name,
                    location=write_op.table_properties.get("location"),
                    schema=input_df.schema,
                    snowpark_session=session,
                    mode="create_or_replace",
                )
                _validate_schema_and_get_writer(
                    input_df, "create_or_replace", snowpark_table_name
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="append",
                    column_order=_column_order_for_write,
                )
            case _:
                exception = SnowparkConnectNotImplementedError(
                    f"Write mode {commands_proto.WriteOperationV2.Mode.Name(write_op.mode)} is not supported"
                )
                attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
                raise exception
    else:
        match write_op.mode:
            case commands_proto.WriteOperationV2.MODE_CREATE:
                _validate_schema_and_get_writer(
                    input_df, "errorifexists", snowpark_table_name
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="errorifexists",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_APPEND:
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if not isinstance(table_schema_or_error, DataType):  # Table not exists
                    exception = AnalysisException(
                        f"[TABLE_OR_VIEW_NOT_FOUND] The table or view `{write_op.table_name}` cannot be found."
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                    raise exception
                if get_table_type(snowpark_table_name, session) not in (
                    "NORMAL",
                    "TABLE",
                ):
                    exception = AnalysisException(
                        f"Table {snowpark_table_name} is not a FDN table"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                    raise exception
                _validate_schema_and_get_writer(
                    input_df, "append", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="append",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_OVERWRITE | commands_proto.WriteOperationV2.MODE_OVERWRITE_PARTITIONS:
                # TODO: handle the filter condition for MODE_OVERWRITE
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if isinstance(table_schema_or_error, DataType):  # Table exists
                    if get_table_type(snowpark_table_name, session) not in (
                        "NORMAL",
                        "TABLE",
                    ):
                        exception = AnalysisException(
                            f"Table {snowpark_table_name} is not a FDN table"
                        )
                        attach_custom_error_code(
                            exception, ErrorCodes.INVALID_OPERATION
                        )
                        raise exception
                else:
                    exception = AnalysisException(
                        f"[TABLE_OR_VIEW_NOT_FOUND] Table {snowpark_table_name} does not exist"
                    )
                    attach_custom_error_code(exception, ErrorCodes.TABLE_NOT_FOUND)
                    raise exception
                _validate_schema_and_get_writer(
                    input_df, "truncate", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="truncate",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_REPLACE:
                table_schema_or_error = _get_table_schema_or_error(
                    snowpark_table_name, session
                )
                if not isinstance(table_schema_or_error, DataType):  # Table not exists
                    exception = AnalysisException(
                        f"Table {snowpark_table_name} does not exist"
                    )
                    attach_custom_error_code(exception, ErrorCodes.TABLE_NOT_FOUND)
                    raise exception
                _validate_schema_and_get_writer(
                    input_df, "replace", snowpark_table_name, table_schema_or_error
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="overwrite",
                    column_order=_column_order_for_write,
                )
            case commands_proto.WriteOperationV2.MODE_CREATE_OR_REPLACE:
                _validate_schema_and_get_writer(
                    input_df, "create_or_replace", snowpark_table_name
                ).saveAsTable(
                    table_name=snowpark_table_name,
                    mode="overwrite",
                    column_order=_column_order_for_write,
                )
            case _:
                exception = SnowparkConnectNotImplementedError(
                    f"Write mode {commands_proto.WriteOperationV2.Mode.Name(write_op.mode)} is not supported"
                )
                attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
                raise exception


def _get_table_schema_or_error(
    snowpark_table_name: str, snowpark_session: snowpark.Session
) -> DataType | SnowparkSQLException:
    try:
        return snowpark_session.table(snowpark_table_name).schema
    except SnowparkSQLException as e:
        return e


def _get_writer_for_table_creation(df: snowpark.DataFrame) -> snowpark.DataFrameWriter:
    # When creating a new table, if case sensitivity is not enabled, we need to rename the columns
    # to upper case so they are case-insensitive in Snowflake.
    if auto_uppercase_column_identifiers():
        for field in df.schema.fields:
            col_name = field.name
            # Uppercasing is fine, regardless of whether the original name was quoted or not.
            # In Snowflake these are equivalent "COL" == COL == col == coL
            uppercased_name = col_name.upper()
            if col_name != uppercased_name:
                df = df.withColumnRenamed(col_name, uppercased_name)
    return df.write


def _validate_schema_and_get_writer(
    input_df: snowpark.DataFrame,
    write_mode: str,
    snowpark_table_name: str,
    table_schema_or_error: DataType | SnowparkSQLException | None = None,
) -> snowpark.DataFrameWriter:
    if write_mode is not None and write_mode.lower() in (
        "replace",
        "create_or_replace",
    ):
        return _get_writer_for_table_creation(input_df)

    table_schema = None
    if table_schema_or_error is not None:
        if isinstance(table_schema_or_error, SnowparkSQLException):
            msg = table_schema_or_error.message
            if "SQL compilation error" in msg and "does not exist" in msg:
                pass
            else:
                attach_custom_error_code(
                    table_schema_or_error, ErrorCodes.INTERNAL_ERROR
                )
                raise table_schema_or_error
        elif isinstance(table_schema_or_error, DataType):
            table_schema = table_schema_or_error
    else:
        try:
            table_schema = (
                get_or_create_snowpark_session().table(snowpark_table_name).schema
            )
        except SnowparkSQLException as e:
            msg = e.message
            if "SQL compilation error" in msg and "does not exist" in msg:
                pass
            else:
                attach_custom_error_code(e, ErrorCodes.INTERNAL_ERROR)
                raise e

    if table_schema is None:
        # If table does not exist, we can skip the schema validation
        return _get_writer_for_table_creation(input_df)

    _validate_schema_for_append(table_schema, input_df.schema, snowpark_table_name)

    # if table exists and case sensitivity is not enabled, we need to rename the columns to match existing table schema
    if auto_uppercase_column_identifiers():

        for field in input_df.schema.fields:
            # Find the matching field in the table schema (case-insensitive)
            col_name = field.name
            renamed = col_name
            matching_field = next(
                (
                    f
                    for f in table_schema.fields
                    if unquote_if_quoted(f.name).upper()
                    == unquote_if_quoted(col_name).upper()
                ),
                None,
            )
            if matching_field is not None and matching_field != col_name:
                renamed = matching_field.name
                input_df = input_df.withColumnRenamed(col_name, renamed)
                # Cast column if type does not match

            if field.datatype != matching_field.datatype:
                if isinstance(matching_field.datatype, StructType):
                    input_df = input_df.withColumn(
                        renamed,
                        col(renamed).cast(matching_field.datatype, rename_fields=True),
                    )
                else:
                    input_df = input_df.withColumn(
                        renamed, col(renamed).cast(matching_field.datatype)
                    )
    return input_df.write


def _validate_schema_for_append(
    table_schema: DataType,
    data_schema: DataType,
    snowpark_table_name: str,
    compare_structs: bool = False,
):
    match (table_schema, data_schema):
        case (_, _) if table_schema == data_schema:
            return

        case (StructType() as table_struct, StructType() as data_struct):

            def _comparable_col_name(col: str) -> str:
                name = col.upper() if auto_uppercase_column_identifiers() else col
                if compare_structs:
                    return name
                else:
                    return unquote_if_quoted(name)

            def invalid_struct_schema():
                exception = AnalysisException(
                    f"Cannot resolve columns for the existing table {snowpark_table_name} ({table_schema.simple_string()}) with the data schema ({data_schema.simple_string()})."
                )
                attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                raise exception

            if len(table_struct.fields) != len(data_struct.fields):
                exception = AnalysisException(
                    f"The column number of the existing table {snowpark_table_name} ({table_schema.simple_string()}) doesn't match the data schema ({data_schema.simple_string()}).)"
                )
                attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
                raise exception

            table_field_names = {
                _comparable_col_name(field.name) for field in table_struct.fields
            }
            data_field_names = {
                _comparable_col_name(field.name) for field in data_struct.fields
            }

            if table_field_names != data_field_names:
                invalid_struct_schema()

            for data_field in data_struct.fields:
                matching_table_field = next(
                    (
                        f
                        for f in table_struct.fields
                        if _comparable_col_name(f.name)
                        == _comparable_col_name(data_field.name)
                    ),
                    None,
                )

                if matching_table_field is None:
                    invalid_struct_schema()
                else:
                    _validate_schema_for_append(
                        matching_table_field.datatype,
                        data_field.datatype,
                        snowpark_table_name,
                        compare_structs=True,
                    )

            return

        case (StringType(), _) if not isinstance(
            data_schema, (StructType, ArrayType, MapType, TimestampType, DateType)
        ):
            return

        case (_, _) if isinstance(table_schema, _NumericType) and isinstance(
            data_schema, _NumericType
        ):
            return

        case (ArrayType() as table_array, ArrayType() as data_array):
            _validate_schema_for_append(
                table_array.element_type, data_array.element_type, snowpark_table_name
            )

        case (MapType() as table_map, MapType() as data_map):
            _validate_schema_for_append(
                table_map.key_type, data_map.key_type, snowpark_table_name
            )
            _validate_schema_for_append(
                table_map.value_type, data_map.value_type, snowpark_table_name
            )

        case (TimestampType(), _) if isinstance(data_schema, (DateType, TimestampType)):
            return
        case (DateType(), _) if isinstance(data_schema, (DateType, TimestampType)):
            return
        case (_, _):
            exception = AnalysisException(
                f"[INCOMPATIBLE_DATA_FOR_TABLE.CANNOT_SAFELY_CAST] Cannot write incompatible data for the table {snowpark_table_name}: Cannot safely cast {data_schema.simple_string()} to {table_schema.simple_string()}"
            )
            attach_custom_error_code(exception, ErrorCodes.INVALID_OPERATION)
            raise exception


def create_iceberg_table(
    snowpark_table_name: str,
    location: str,
    schema: StructType,
    snowpark_session: snowpark.Session,
    mode: str = "create",
):
    table_schema = [
        f"{spark_to_sf_single_id(unquote_if_quoted(field.name), is_column = True)} {snowpark_to_iceberg_type(field.datatype)}"
        for field in schema.fields
    ]

    location = (
        location
        if location is not None and location != ""
        else f"SNOWPARK_CONNECT_DEFAULT_LOCATION/{snowpark_table_name}"
    )
    base_location = f"BASE_LOCATION = '{location}'"

    config_external_volume = sessions_config.get(get_session_id(), {}).get(
        "snowpark.connect.iceberg.external_volume", None
    )
    external_volume = (
        ""
        if config_external_volume is None or config_external_volume == ""
        else f"EXTERNAL_VOLUME = '{config_external_volume}'"
    )

    match mode:
        case "create":
            create_sql = "CREATE"
        case "replace":
            # There's no replace for iceberg table, so we use create or replace
            create_sql = "CREATE OR REPLACE"
        case "create_or_replace":
            create_sql = "CREATE OR REPLACE"
        case _:
            exception = SnowparkConnectNotImplementedError(
                f"Write mode {mode} is not supported for iceberg table"
            )
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
            raise exception
    sql = f"""
        {create_sql} ICEBERG TABLE {snowpark_table_name} ({",".join(table_schema)})
        CATALOG = 'SNOWFLAKE'
        {external_volume}
        {base_location};
        """
    snowpark_session.sql(sql).collect()


def rewrite_df(input_df: snowpark.DataFrame, source: str) -> snowpark.DataFrame:
    """
    Rewrite dataframe if needed.
        json: construct the dataframe to 1 column in json format
            1. Append columns which represents the column name
            2. Use object_construct to aggregate the dataframe into 1 column

    """
    if source != "json":
        return input_df
    rand_salt = random_string(10, "_")
    rewritten_df = input_df.with_columns(
        [co + rand_salt for co in input_df.columns],
        [lit(unquote_if_quoted(co)) for co in input_df.columns],
    )
    construct_key_values = []
    for co in input_df.columns:
        construct_key_values.append(col(co + rand_salt))
        construct_key_values.append(col(co))
    return rewritten_df.select(object_construct(*construct_key_values))


def handle_column_names(
    container: DataFrameContainer, source: str
) -> snowpark.DataFrame:
    """
    Handle column names before write so they match spark schema.
    """
    df = container.dataframe
    if source == "jdbc":
        # don't change column names for jdbc sources as we directly use spark column names for writing to the destination tables.
        return df
    column_map = container.column_map

    for column in column_map.columns:
        df = df.withColumnRenamed(
            column.snowpark_name, quote_name_without_upper_casing(column.spark_name)
        )
    return df


def store_files_locally(
    stage_path: str, target_path: str, overwrite: bool, session: snowpark.Session
) -> None:
    target_path = convert_file_prefix_path(target_path)
    real_path = (
        Path(target_path).expanduser()
        if target_path.startswith("~/")
        else Path(target_path)
    )
    if overwrite and os.path.isdir(target_path):
        _truncate_directory(real_path)
    # Per Snowflake docs: "The command does not preserve stage directory structure when transferring files to your client machine"
    # https://docs.snowflake.com/en/sql-reference/sql/get
    # Preserve directory structure under stage_path by listing files and
    # downloading each into its corresponding local subdirectory when partition subdirs exist.
    # Otherwise, fall back to a direct GET which flattens.

    # TODO(SNOW-2326973): This can be parallelized further. Its not done here because it only affects
    # write to local storage.

    ls_dataframe = session.sql(f"LS {stage_path}")
    ls_iterator = ls_dataframe.toLocalIterator()

    # Build a normalized base prefix from stage_path to compute relatives
    # Example: stage_path='@MY_STAGE/prefix' -> base_prefix='my_stage/prefix/'
    base_prefix = stage_path.lstrip("@").rstrip("/") + "/"
    base_prefix_lower = base_prefix.lower()

    # Group by parent directory under the base prefix, then issue a GET per directory.
    # This gives a small parallelism advantage if we have many files per partition directory.
    parent_dirs: set[str] = set()
    for row in ls_iterator:
        name: str = row[0]
        name_lower = name.lower()
        rel_start = name_lower.find(base_prefix_lower)
        relative = name[rel_start + len(base_prefix) :] if rel_start != -1 else name
        parent_dir = os.path.dirname(relative)
        if parent_dir and parent_dir != ".":
            parent_dirs.add(parent_dir)

    # If no parent directories were discovered (non-partitioned unload prefix), use direct GET.
    if not parent_dirs:
        snowpark.file_operation.FileOperation(session).get(stage_path, str(real_path))
        return

    file_op = snowpark.file_operation.FileOperation(session)
    for parent_dir in sorted(parent_dirs):
        local_dir = real_path / parent_dir
        os.makedirs(local_dir, exist_ok=True)

        src_dir = f"@{base_prefix}{parent_dir}"
        file_op.get(src_dir, str(local_dir))


def _truncate_directory(directory_path: Path) -> None:
    if not directory_path.exists():
        exception = FileNotFoundError(
            f"The specified directory {directory_path} does not exist."
        )
        attach_custom_error_code(exception, ErrorCodes.INVALID_INPUT)
        raise exception
    # Iterate over all the files and directories in the specified directory
    for file in directory_path.iterdir():
        # Check if it is a file or directory and remove it
        if file.is_file() or file.is_symlink():
            file.unlink()
        elif file.is_dir():
            shutil.rmtree(file)
