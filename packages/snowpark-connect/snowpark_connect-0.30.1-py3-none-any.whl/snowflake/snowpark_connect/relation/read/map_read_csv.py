#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import copy
from typing import Any

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark.dataframe_reader import DataFrameReader
from snowflake.snowpark.types import StringType, StructField, StructType
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.read.map_read import CsvReaderConfig
from snowflake.snowpark_connect.relation.read.metadata_utils import (
    add_filename_metadata_to_reader,
    get_non_metadata_fields,
)
from snowflake.snowpark_connect.relation.read.utils import (
    get_spark_column_names_from_snowpark_columns,
    rename_columns_as_snowflake_standard,
)
from snowflake.snowpark_connect.utils.io_utils import cached_file_format
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_read_csv(
    rel: relation_proto.Relation,
    schema: snowpark.types.StructType | None,
    session: snowpark.Session,
    paths: list[str],
    options: CsvReaderConfig,
) -> DataFrameContainer:
    """
    Read a CSV file into a Snowpark DataFrame.

    We leverage the stage that is already created in the map_read function that
    calls this.
    """

    if rel.read.is_streaming is True:
        # TODO: Structured streaming implementation.
        raise SnowparkConnectNotImplementedError(
            "Streaming is not supported for CSV files."
        )
    else:
        snowpark_options = options.convert_to_snowpark_args()
        parse_header = snowpark_options.get("PARSE_HEADER", False)
        file_format_options = _parse_csv_snowpark_options(snowpark_options)
        file_format = cached_file_format(session, "csv", file_format_options)

        snowpark_read_options = dict()
        snowpark_read_options["FORMAT_NAME"] = file_format
        snowpark_read_options["ENFORCE_EXISTING_FILE_FORMAT"] = True
        snowpark_read_options["INFER_SCHEMA"] = snowpark_options.get(
            "INFER_SCHEMA", False
        )
        snowpark_read_options["PATTERN"] = snowpark_options.get("PATTERN", None)

        raw_options = rel.read.data_source.options

        if schema is None or (
            parse_header and raw_options.get("enforceSchema", "True").lower() == "false"
        ):  # Schema has to equals to header's format
            reader = add_filename_metadata_to_reader(
                session.read.options(snowpark_options), raw_options
            )
        else:
            reader = add_filename_metadata_to_reader(
                session.read.options(snowpark_options).schema(schema), raw_options
            )
        df = read_data(
            reader,
            schema,
            session,
            paths[0],
            file_format_options,
            snowpark_read_options,
            raw_options,
            parse_header,
        )
        if len(paths) > 1:
            # TODO: figure out if this is what Spark does.
            for p in paths[1:]:
                df = df.union_all(reader.csv(p))

        if schema is None:
            df = df.select(
                [snowpark_fn.col(c).cast("STRING").alias(c) for c in df.schema.names]
            )

        spark_column_names = get_spark_column_names_from_snowpark_columns(df.columns)

        renamed_df, snowpark_column_names = rename_columns_as_snowflake_standard(
            df, rel.common.plan_id
        )
        return DataFrameContainer.create_with_column_mapping(
            dataframe=renamed_df,
            spark_column_names=spark_column_names,
            snowpark_column_names=snowpark_column_names,
            snowpark_column_types=[f.datatype for f in df.schema.fields],
        )


_csv_file_format_allowed_options = {
    "COMPRESSION",
    "RECORD_DELIMITER",
    "FIELD_DELIMITER",
    "MULTI_LINE",
    "FILE_EXTENSION",
    "PARSE_HEADER",
    "SKIP_HEADER",
    "SKIP_BLANK_LINES",
    "DATE_FORMAT",
    "TIME_FORMAT",
    "TIMESTAMP_FORMAT",
    "BINARY_FORMAT",
    "ESCAPE",
    "ESCAPE_UNENCLOSED_FIELD",
    "TRIM_SPACE",
    "FIELD_OPTIONALLY_ENCLOSED_BY",
    "NULL_IF",
    "ERROR_ON_COLUMN_COUNT_MISMATCH",
    "REPLACE_INVALID_CHARACTERS",
    "EMPTY_FIELD_AS_NULL",
    "SKIP_BYTE_ORDER_MARK",
    "ENCODING",
}


def _parse_csv_snowpark_options(snowpark_options: dict[str, Any]) -> dict[str, Any]:
    file_format_options = dict()
    for key, value in snowpark_options.items():
        upper_key = key.upper()
        if upper_key in _csv_file_format_allowed_options:
            file_format_options[upper_key] = value

    # This option has to be removed, because we cannot use at the same time predefined file format and parse_header option
    # Such combination causes snowpark to raise SQL compilation error: Invalid file format "PARSE_HEADER" is only allowed for CSV INFER_SCHEMA and MATCH_BY_COLUMN_NAME
    parse_header = file_format_options.get("PARSE_HEADER", False)
    if parse_header:
        file_format_options["SKIP_HEADER"] = 1
        del file_format_options["PARSE_HEADER"]

    return file_format_options


def get_header_names(
    session: snowpark.Session,
    path: list[str],
    file_format_options: dict,
    snowpark_read_options: dict,
) -> list[str]:
    no_header_file_format_options = copy.copy(file_format_options)
    no_header_file_format_options["PARSE_HEADER"] = False
    no_header_file_format_options.pop("SKIP_HEADER", None)

    file_format = cached_file_format(session, "csv", no_header_file_format_options)
    no_header_snowpark_read_options = copy.copy(snowpark_read_options)
    no_header_snowpark_read_options["FORMAT_NAME"] = file_format
    no_header_snowpark_read_options.pop("INFER_SCHEMA", None)

    header_df = session.read.options(no_header_snowpark_read_options).csv(path).limit(1)
    header_data = header_df.collect()[0]
    return [
        f'"{header_data[i]}"'
        for i in range(len(header_df.schema.fields))
        if header_data[i] is not None
    ]


def read_data(
    reader: DataFrameReader,
    schema: snowpark.types.StructType | None,
    session: snowpark.Session,
    path: list[str],
    file_format_options: dict,
    snowpark_read_options: dict,
    raw_options: dict,
    parse_header: bool,
) -> snowpark.DataFrame:
    df = reader.csv(path)
    filename = path.strip("/").split("/")[-1]
    non_metadata_fields = get_non_metadata_fields(df.schema.fields)

    if schema is not None:
        if len(schema.fields) != len(non_metadata_fields):
            raise Exception(f"csv load from {filename} failed.")
        if raw_options.get("enforceSchema", "True").lower() == "false":
            for i in range(len(schema.fields)):
                if (
                    schema.fields[i].name != non_metadata_fields[i].name
                    and f'"{schema.fields[i].name}"' != non_metadata_fields[i].name
                ):
                    raise Exception("CSV header does not conform to the schema")
        return df

    headers = get_header_names(
        session, path, file_format_options, snowpark_read_options
    )

    df_schema_fields = non_metadata_fields
    if len(headers) == len(df_schema_fields) and parse_header:
        return df.select(
            [
                snowpark_fn.col(df_schema_fields[i].name).alias(headers[i])
                for i in range(len(headers))
            ]
        )
    # Handle mismatch in column count between header and data
    elif (
        len(df_schema_fields) == 1
        and df_schema_fields[0].name.upper() == "C1"
        and parse_header
        and len(headers) != len(df_schema_fields)
    ):
        df = reader.schema(
            StructType([StructField(h, StringType(), True) for h in headers])
        ).csv(path)
    elif not parse_header and len(headers) != len(df_schema_fields):
        return df.select([df_schema_fields[i].name for i in range(len(headers))])
    elif parse_header and len(headers) != len(df_schema_fields):
        return df.select(
            [
                snowpark_fn.col(df_schema_fields[i].name).alias(headers[i])
                for i in range(len(headers))
            ]
        )
    return df
