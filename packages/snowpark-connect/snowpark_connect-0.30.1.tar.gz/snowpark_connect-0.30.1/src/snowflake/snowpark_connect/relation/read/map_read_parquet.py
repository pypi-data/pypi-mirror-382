#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import collections
import re
from collections.abc import Callable

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark import (
    DataFrame,
    DataFrameReader,
    Session,
    functions as snowpark_fn,
)
from snowflake.snowpark._internal.analyzer import analyzer_utils
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
)
from snowflake.snowpark.column import METADATA_FILENAME
from snowflake.snowpark.types import DataType, DoubleType, IntegerType, StringType
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.read.metadata_utils import (
    add_filename_metadata_to_reader,
)
from snowflake.snowpark_connect.relation.read.reader_config import ReaderWriterConfig
from snowflake.snowpark_connect.relation.read.utils import (
    rename_columns_as_snowflake_standard,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_read_parquet(
    rel: relation_proto.Relation,
    schema: str | None,
    session: snowpark.Session,
    paths: list[str],
    options: ReaderWriterConfig,
) -> DataFrameContainer:
    """Read a Parquet file into a Snowpark DataFrame."""

    if rel.read.is_streaming is True:
        raise SnowparkConnectNotImplementedError(
            "Streaming is not supported for Parquet files."
        )

    snowpark_options = options.convert_to_snowpark_args()
    raw_options = rel.read.data_source.options
    assert schema is None, "Read PARQUET does not support user schema"
    assert len(paths) > 0, "Read PARQUET expects at least one path"

    reader = add_filename_metadata_to_reader(
        session.read.options(snowpark_options), raw_options
    )

    if len(paths) == 1:
        df = _read_parquet_with_partitions(session, reader, paths[0])
    else:
        is_merge_schema = options.config.get("mergeschema")
        df = _read_parquet_with_partitions(session, reader, paths[0])
        schema_cols = df.columns
        for p in paths[1:]:
            reader._user_schema = None
            df = df.union_all_by_name(
                _read_parquet_with_partitions(session, reader, p),
                allow_missing_columns=True,
            )
        if not is_merge_schema:
            df = df.select(*schema_cols)

    renamed_df, snowpark_column_names = rename_columns_as_snowflake_standard(
        df, rel.common.plan_id
    )
    return DataFrameContainer.create_with_column_mapping(
        dataframe=renamed_df,
        spark_column_names=[analyzer_utils.unquote_if_quoted(c) for c in df.columns],
        snowpark_column_names=snowpark_column_names,
        snowpark_column_types=[f.datatype for f in df.schema.fields],
    )


def _read_parquet_with_partitions(
    session: Session, reader: DataFrameReader, path: str
) -> DataFrame:
    """Reads parquet files and adds partition columns from subdirectories."""

    partition_columns, inferred_types = _discover_partition_columns(session, path)
    df = reader.with_metadata(METADATA_FILENAME).parquet(path)

    if not partition_columns:
        return df.drop(METADATA_FILENAME)

    for col_name in partition_columns:
        quoted_col_name = quote_name_without_upper_casing(col_name)
        escaped_col_name = re.escape(col_name)
        regex_pattern = rf"{escaped_col_name}=([^/]+)"

        raw_value = snowpark_fn.regexp_extract(METADATA_FILENAME, regex_pattern, 1)
        value_or_null = snowpark_fn.when(raw_value == "", None).otherwise(raw_value)

        df = df.with_column(
            quoted_col_name, snowpark_fn.cast(value_or_null, inferred_types[col_name])
        )

    return df.drop(METADATA_FILENAME)


def _extract_partitions_from_path(path: str) -> dict[str, str]:
    """Extracts partition key-value pairs from a path."""
    partitions = {}
    for segment in path.split("/"):
        if "=" in segment:
            col_name, value = _parse_partition_column(segment)
            if col_name and value:
                partitions[col_name] = value
    return partitions


def _discover_partition_columns(
    session: Session, stage_path: str
) -> tuple[list[str], dict[str, DataType]]:
    """Discovers partition columns by analyzing subdirectory structure."""

    partition_columns_values = collections.defaultdict(set)
    dir_level_to_column_name = {}
    base_partitions = _extract_partitions_from_path(stage_path)

    path_segments_to_skip = len(stage_path.strip("/").split("/"))
    if stage_path.startswith("@"):
        path_segments_to_skip = 1
        stage_parts = stage_path.split("/", 2)
        if len(stage_parts) > 2:
            additional_segments = len(stage_parts[2].strip("/").split("/"))
            path_segments_to_skip += additional_segments

    ls_result = session.sql(f"LS {stage_path}").collect()
    if ls_result:
        file_names = [row[0] for row in ls_result]

        for file_path in file_names:
            path_parts = file_path.strip("/").split("/")
            path_segments_to_analyze = path_parts[path_segments_to_skip:]

            for i, part in enumerate(path_segments_to_analyze):
                if "=" in part and not part.endswith(".parquet"):
                    key, value = part.split("=", 1)

                    if key in base_partitions:
                        continue

                    if i not in dir_level_to_column_name:
                        dir_level_to_column_name[i] = key
                    elif dir_level_to_column_name[i] != key:
                        raise ValueError(
                            f"Conflicting partition column names detected: '{dir_level_to_column_name[i]}' and '{key}' "
                            f"at the same directory level"
                        )

                    partition_columns_values[key].add(value)

    seen_columns = set()
    for level in sorted(dir_level_to_column_name.keys()):
        col_name = dir_level_to_column_name[level]
        if col_name in seen_columns:
            raise ValueError(
                f"Found partition column '{col_name}' at multiple directory levels. "
                f"A partition column can only appear at a single level."
            )
        seen_columns.add(col_name)

    ordered_columns = [
        dir_level_to_column_name[level]
        for level in sorted(dir_level_to_column_name.keys())
    ]

    inferred_types = {
        col_name: _infer_partition_column_type(partition_columns_values[col_name])
        for col_name in ordered_columns
    }

    return ordered_columns, inferred_types


def _infer_partition_column_type(values: set[str]) -> DataType:
    def _is_castable(value: str, type_: Callable) -> bool:
        try:
            type_(value)
            return True
        except ValueError:
            return False

    if all(_is_castable(value, int) for value in values):
        return IntegerType()
    if all(_is_castable(value, float) for value in values):
        return DoubleType()
    return StringType()


def _parse_partition_column(name: str) -> tuple[str, str]:
    """Extracts column name and partition value from a path segment."""
    col_name, partition_value = name.split("=", maxsplit=1)

    return col_name, partition_value
