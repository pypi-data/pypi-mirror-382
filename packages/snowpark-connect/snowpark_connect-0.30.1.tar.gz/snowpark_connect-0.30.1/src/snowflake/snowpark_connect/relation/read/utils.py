#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import functools
import re
import time
from collections.abc import Callable
from typing import (  # noqa: F401
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Iterator,
    List,
    NewType,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer import analyzer_utils
from snowflake.snowpark.exceptions import SnowparkClientException
from snowflake.snowpark_connect.column_name_handler import (
    make_column_names_snowpark_compatible,
)
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger

STATEMENT_PARAMS_DATA_SOURCE = "SNOWPARK_PYTHON_DATASOURCE"
DATA_SOURCE_DBAPI_SIGNATURE = "DataFrameReader.dbapi"
DATA_SOURCE_SQL_COMMENT = (
    f"/* Python:snowflake.snowpark.{DATA_SOURCE_DBAPI_SIGNATURE} */"
)

INDEXED_COLUMN_NAME_PATTERN = re.compile(r"(^\"c)(\d+)(\"$)")


def subtract_one(match: re.Match[str]) -> str:
    """Spark column names are 0 indexed, Snowpark is 1 indexed."""
    return f"_c{str(int(match.group(2)) - 1)}"


def get_spark_column_names_from_snowpark_columns(
    snowpark_column_names: List[str],
) -> List[str]:
    return [
        analyzer_utils.unquote_if_quoted(
            INDEXED_COLUMN_NAME_PATTERN.sub(subtract_one, c)
        )
        for c in snowpark_column_names
    ]


def rename_columns_as_snowflake_standard(
    df: snowpark.DataFrame, plan_id: int
) -> tuple[snowpark.DataFrame, list[str]]:
    """
    Renames the columns of a Snowflake DataFrame to follow a standard format.
    Args:
        df (snowpark.DataFrame): The input Snowflake DataFrame.

    Returns:
        tuple[snowpark.DataFrame, list[str]]: A tuple containing the modified DataFrame
        with renamed columns and a list of the new column names.
    """

    if df.columns is None or len(df.columns) == 0:
        return df, []

    new_columns = make_column_names_snowpark_compatible(df.columns, plan_id)
    return (
        df.select(
            *(df.col(orig).alias(alias) for orig, alias in zip(df.columns, new_columns))
        ),
        new_columns,
    )


class Connection(Protocol):
    """External datasource connection created from user-input create_connection function."""

    def cursor(self) -> "Cursor":
        pass

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass


class Cursor(Protocol):
    """Cursor created from external datasource connection"""

    def execute(self, sql: str, *params: Any) -> "Cursor":
        pass

    def fetchall(self):
        pass

    def fetchone(self):
        pass

    def close(self):
        pass


def exponential_backoff(
    func: Callable | None = None,
    max_retry_count: int = 3,
    initial_retry_delay_ms: int = 50,
    exponential_backoff_base: int = 2,
) -> Callable:
    if func is None:
        return functools.partial(
            exponential_backoff,
            max_retry_count=max_retry_count,
            initial_retry_delay_ms=initial_retry_delay_ms,
            exponential_backoff_base=exponential_backoff_base,
        )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        error = None
        for retry_count in range(max_retry_count):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = e

                delay_ms = (
                    exponential_backoff_base**retry_count * initial_retry_delay_ms
                )
                time.sleep(delay_ms / 1000.0)
                logger.debug(
                    f"Function '{func.__name__}' failed with {error.__repr__()}, retry count: {retry_count}, retrying ..."
                )
        error = SnowparkClientException(
            message=f"failed to run '{func.__name__}', got {error.__repr__()}"
        )
        logger.debug(
            f"Function '{func.__name__}' failed with {error.__repr__()}, exceed max retry time"
        )

        return error

    return wrapper
