#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from snowflake import snowpark
from snowflake.snowpark.types import StructField, StructType

if TYPE_CHECKING:
    from snowflake.snowpark_connect.column_name_handler import ColumnNameMap


class DataFrameContainer:
    """
    A container class that wraps a Snowpark DataFrame along with additional metadata.

    This class provides a unified interface for managing Snowpark DataFrames along with
    their column mappings, schema information, and metadata.
    """

    def __init__(
        self,
        dataframe: snowpark.DataFrame,
        column_map: ColumnNameMap | None = None,
        table_name: str | None = None,
        alias: str | None = None,
        cached_schema_getter: Callable[[], StructType] | None = None,
        partition_hint: int | None = None,
    ) -> None:
        """
        Initialize a new DataFrameContainer.

        Args:
            dataframe: The underlying Snowpark DataFrame
            column_map: Optional column name mapping
            table_name: Optional table name for the DataFrame
            alias: Optional alias for the DataFrame
            cached_schema_getter: Optional function to get cached schema
            partition_hint: Optional partition count from repartition() operations
        """
        self._dataframe = dataframe
        self._column_map = self._create_default_column_map(column_map)
        self._table_name = table_name
        self._alias = alias
        self._partition_hint = partition_hint

        if cached_schema_getter is not None:
            self._apply_cached_schema_getter(cached_schema_getter)

    @classmethod
    def create_with_column_mapping(
        cls,
        dataframe: snowpark.DataFrame,
        spark_column_names: list[str],
        snowpark_column_names: list[str],
        snowpark_column_types: list | None = None,
        column_metadata: dict | None = None,
        column_qualifiers: list[list[str]] | None = None,
        parent_column_name_map: ColumnNameMap | None = None,
        table_name: str | None = None,
        alias: str | None = None,
        cached_schema_getter: Callable[[], StructType] | None = None,
        partition_hint: int | None = None,
    ) -> DataFrameContainer:
        """
        Create a new container with complete column mapping configuration.

        Args:
            dataframe: The underlying Snowpark DataFrame
            spark_column_names: List of Spark column names
            snowpark_column_names: List of corresponding Snowpark column names
            snowpark_column_types: Optional list of column types
            column_metadata: Optional metadata dictionary
            column_qualifiers: Optional column qualifiers
            parent_column_name_map: Optional parent column name map
            table_name: Optional table name
            alias: Optional alias
            cached_schema_getter: Optional function to get cached schema
            partition_hint: Optional partition count from repartition() operations

        Returns:
            A new DataFrameContainer instance

        Raises:
            AssertionError: If column names and types don't match expected lengths
        """
        # Validate inputs
        cls._validate_column_mapping_inputs(
            spark_column_names, snowpark_column_names, snowpark_column_types
        )

        column_map = cls._create_column_map(
            spark_column_names,
            snowpark_column_names,
            column_metadata,
            column_qualifiers,
            parent_column_name_map,
        )

        # Determine the schema getter to use
        final_schema_getter = None

        if cached_schema_getter is not None:
            # Use the provided schema getter
            final_schema_getter = cached_schema_getter
        elif snowpark_column_types is not None:
            # Create schema from types and wrap in function
            schema = cls._create_schema_from_types(
                snowpark_column_names, snowpark_column_types
            )
            if schema is not None:

                def get_schema():
                    return schema

                final_schema_getter = get_schema

        return cls(
            dataframe=dataframe,
            column_map=column_map,
            table_name=table_name,
            alias=alias,
            cached_schema_getter=final_schema_getter,
            partition_hint=partition_hint,
        )

    @property
    def dataframe(self) -> snowpark.DataFrame:
        """Get the underlying Snowpark DataFrame."""
        # Ensure the DataFrame has the _column_map attribute for backward compatibility
        # Some of the snowpark code needs references to _column_map
        self._dataframe._column_map = self._column_map
        return self._dataframe

    @property
    def column_map(self) -> ColumnNameMap:
        """Get the column name mapping."""
        return self._column_map

    @column_map.setter
    def column_map(self, value: ColumnNameMap) -> None:
        """Set the column name mapping."""
        self._column_map = value

    @property
    def table_name(self) -> str | None:
        """Get the table name."""
        return self._table_name

    @table_name.setter
    def table_name(self, value: str | None) -> None:
        """Set the table name."""
        self._table_name = value

    @property
    def alias(self) -> str | None:
        """Get the alias name."""
        return self._alias

    @alias.setter
    def alias(self, value: str | None) -> None:
        """Set the alias name."""
        self._alias = value

    @property
    def partition_hint(self) -> int | None:
        """Get the partition hint count."""
        return self._partition_hint

    @partition_hint.setter
    def partition_hint(self, value: int | None) -> None:
        """Set the partition hint count."""
        self._partition_hint = value

    def _create_default_column_map(
        self, column_map: ColumnNameMap | None
    ) -> ColumnNameMap:
        """Create a default column map if none provided."""
        if column_map is not None:
            return column_map

        from snowflake.snowpark_connect.column_name_handler import ColumnNameMap

        return ColumnNameMap([], [])

    def _apply_cached_schema_getter(
        self, schema_getter: Callable[[], StructType]
    ) -> None:
        """Apply a cached schema getter to the dataframe."""
        from snowflake.snowpark_connect.column_name_handler import set_schema_getter

        set_schema_getter(self._dataframe, schema_getter)

    @staticmethod
    def _validate_column_mapping_inputs(
        spark_column_names: list[str],
        snowpark_column_names: list[str],
        snowpark_column_types: list | None = None,
    ) -> None:
        """
        Validate inputs for column mapping creation.

        Raises:
            AssertionError: If validation fails
        """
        assert len(snowpark_column_names) == len(
            spark_column_names
        ), "Number of Spark column names must match number of columns in DataFrame"

        if snowpark_column_types is not None:
            assert len(snowpark_column_names) == len(
                snowpark_column_types
            ), "Number of Snowpark column names and types must match"

    @staticmethod
    def _create_column_map(
        spark_column_names: list[str],
        snowpark_column_names: list[str],
        column_metadata: dict | None = None,
        column_qualifiers: list[list[str]] | None = None,
        parent_column_name_map: ColumnNameMap | None = None,
    ) -> ColumnNameMap:
        """Create a ColumnNameMap with the provided configuration."""
        from snowflake.snowpark_connect.column_name_handler import ColumnNameMap

        return ColumnNameMap(
            spark_column_names,
            snowpark_column_names,
            column_metadata=column_metadata,
            column_qualifiers=column_qualifiers,
            parent_column_name_map=parent_column_name_map,
        )

    @staticmethod
    def _create_schema_from_types(
        snowpark_column_names: list[str],
        snowpark_column_types: list | None,
    ) -> StructType | None:
        """
        Create a StructType schema from column names and types.

        Returns:
            StructType if types are provided, None otherwise
        """
        if snowpark_column_types is None:
            return None

        return StructType(
            [
                StructField(name, column_type, _is_column=False)
                for name, column_type in zip(
                    snowpark_column_names, snowpark_column_types
                )
            ]
        )
