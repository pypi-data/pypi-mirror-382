#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap


class EmptyDataFrame(snowpark.DataFrame):

    __name__ = "DataFrame"

    def __init__(self) -> None:
        self._column_map = ColumnNameMap([], [])
        self._table_name = None

    columns = []
    schema = snowpark.types.StructType([])
