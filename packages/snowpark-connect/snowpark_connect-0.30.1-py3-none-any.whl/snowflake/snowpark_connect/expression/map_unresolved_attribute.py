#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import re

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
from pyspark.errors.exceptions.connect import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
)
from snowflake.snowpark.exceptions import SnowparkSQLException
from snowflake.snowpark.types import ArrayType, LongType, MapType, StructType
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    get_current_grouping_columns,
    get_is_evaluating_sql,
    get_outer_dataframes,
    get_plan_id_map,
    is_lambda_being_resolved,
    resolve_lca_alias,
)
from snowflake.snowpark_connect.utils.identifiers import (
    split_fully_qualified_spark_name,
)

SPARK_QUOTED = re.compile("^(`.*`)$", re.DOTALL)


def _get_catalog_database_from_column_map(
    column_name: str, column_map: ColumnNameMap
) -> dict[str, str]:
    """
    Get catalog/database info from the column map for a given column name.
    This replaces the previous extraction logic by looking up stored metadata.

    Returns:
        dict: catalog_database_info containing catalog/database metadata if found
    """
    catalog_database_info = {}

    # Look up in the column map using case-sensitive or case-insensitive matching
    matching_columns = []
    if hasattr(column_map, "is_case_sensitive") and column_map.is_case_sensitive():
        matching_columns = column_map.spark_to_col.get(column_name, [])
    elif hasattr(column_map, "uppercase_spark_to_col"):
        matching_columns = column_map.uppercase_spark_to_col.get(
            column_name.upper(), []
        )
    elif hasattr(column_map, "spark_to_col"):
        matching_columns = column_map.spark_to_col.get(column_name, [])

    # If we found a matching column with catalog/database info, use it
    for col_names in matching_columns:
        if col_names.catalog_info and col_names.database_info:
            catalog_database_info = {
                "catalog": col_names.catalog_info,
                "database": col_names.database_info,
            }
            break

    return catalog_database_info


def map_unresolved_attribute(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[str, TypedColumn]:
    original_attr_name = exp.unresolved_attribute.unparsed_identifier
    name_parts = split_fully_qualified_spark_name(original_attr_name)

    assert len(name_parts) > 0, f"Unable to parse input attribute: {original_attr_name}"

    # Special handling for Spark's automatic grouping__id column
    # In Spark SQL, when using GROUP BY CUBE/ROLLUP/GROUPING SETS, an automatic
    # virtual column called 'grouping__id' (with double underscores) is available.
    # In Snowflake, we need to convert this to a GROUPING_ID() function call.
    if len(name_parts) == 1 and name_parts[0].lower() == "grouping__id":
        grouping_spark_columns = get_current_grouping_columns()
        if not grouping_spark_columns:
            # grouping__id can only be used with GROUP BY CUBE/ROLLUP/GROUPING SETS
            raise AnalysisException(
                "[MISSING_GROUP_BY] grouping__id can only be used with GROUP BY (CUBE | ROLLUP | GROUPING SETS)"
            )
        # Convert to GROUPING_ID() function call with the grouping columns
        # Map Spark column names to Snowpark column names
        snowpark_cols = []
        for spark_col_name in grouping_spark_columns:
            # Get the Snowpark column name from the mapping
            snowpark_name = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    spark_col_name
                )
            )
            if not snowpark_name:
                raise AnalysisException(
                    f"[INTERNAL_ERROR] Cannot find Snowpark column mapping for grouping column '{spark_col_name}'"
                )
            snowpark_cols.append(snowpark_fn.col(snowpark_name))

        # Call GROUPING_ID with all grouping columns using Snowpark names
        result_col = snowpark_fn.grouping_id(*snowpark_cols)

        # TypedColumn expects a callable that returns a list of types
        # GROUPING_ID returns a BIGINT (LongType) in both Spark and Snowflake
        # representing the bit vector of grouping indicators
        typed_col = TypedColumn(result_col, lambda: [LongType()])
        return ("grouping__id", typed_col)

    # Validate that DataFrame API doesn't allow catalog.database.column patterns
    # These patterns should only work in SQL, not DataFrame API
    if len(name_parts) >= 4:
        # For 4+ parts, check if this looks like catalog.database.column.field
        # (as opposed to a valid table.column.field pattern)

        # Heuristic: if the pattern looks like catalog.database.column.field,
        # reject it in DataFrame API context (but allow in SQL)

        # Check if first part looks like a catalog name (not a column)
        first_part = name_parts[0]
        first_part_snowpark = (
            column_mapping.get_snowpark_column_name_from_spark_column_name(
                first_part, allow_non_exists=True
            )
        )

        # If first part is not a column and we have 4+ parts, check if it's a catalog reference
        if first_part_snowpark is None and len(name_parts) >= 4:
            # Import here to avoid circular import issues
            from snowflake.snowpark_connect.relation.catalogs import CATALOGS

            # Check if the first part is a registered catalog name OR looks like a catalog pattern
            is_registered_catalog = first_part.lower() in CATALOGS
            is_catalog_like = (
                # Contains "catalog" in the name
                "catalog" in first_part.lower()
                # Follows catalog naming patterns (no numbers, shorter descriptive names)
                or (
                    len(first_part) < 20
                    and not any(char.isdigit() for char in first_part)
                    and not first_part.startswith("mydb")
                    and not first_part.endswith(  # Skip test-generated database names
                        "_dbmsu"
                    )
                )  # Skip test-generated database names
            )

            is_catalog = is_registered_catalog or is_catalog_like

            if is_catalog:
                # This looks like a catalog.database.column.field pattern
                raise AnalysisException(
                    f"[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column or function parameter with name `{original_attr_name}` cannot be resolved. "
                    f"Cross-catalog column references are not supported in DataFrame API."
                )

    attr_name = ".".join(name_parts)

    has_plan_id = exp.unresolved_attribute.HasField("plan_id")

    if has_plan_id:
        plan_id = exp.unresolved_attribute.plan_id
        target_df_container = get_plan_id_map(plan_id)
        target_df = target_df_container.dataframe
        assert (
            target_df is not None
        ), f"resolving an attribute of a unresolved dataframe {plan_id}"
        column_mapping = target_df_container.column_map
        typer = ExpressionTyper(target_df)

    def get_col(snowpark_name):
        return (
            snowpark_fn.col(snowpark_name)
            if not has_plan_id
            else target_df.col(snowpark_name)
        )

    # Check if regex column names are enabled and this is a quoted identifier
    # We need to check the original attribute name before split_fully_qualified_spark_name processes it
    if (
        get_is_evaluating_sql()
        and global_config.spark_sql_parser_quotedRegexColumnNames
        and SPARK_QUOTED.match(original_attr_name)
    ):
        # Extract regex pattern by removing backticks
        regex_pattern = original_attr_name[1:-1]  # Remove first and last backtick

        # Get all available column names from the column mapping
        available_columns = column_mapping.get_spark_columns()

        # Match the regex pattern against available columns
        matched_columns = []
        try:
            compiled_regex = re.compile(
                regex_pattern,
                re.IGNORECASE if not global_config.spark_sql_caseSensitive else 0,
            )
            for col_name in available_columns:
                if compiled_regex.fullmatch(col_name):
                    matched_columns.append(col_name)
        except re.error as e:
            raise AnalysisException(f"Invalid regex pattern '{regex_pattern}': {e}")

        if not matched_columns:
            # Keep the improved error message for SQL regex patterns
            # This is only hit for SQL queries like SELECT `(e|f)` FROM table
            # when spark.sql.parser.quotedRegexColumnNames is enabled
            raise AnalysisException(
                f"No columns match the regex pattern '{regex_pattern}'. "
                f"Snowflake SQL does not support SELECT statements with no columns. "
                f"Please ensure your regex pattern matches at least one column. "
                f"Available columns: {', '.join(available_columns[:10])}{'...' if len(available_columns) > 10 else ''}"
            )

        # When multiple columns match, we need to signal that this should expand to multiple columns
        # Since map_unresolved_attribute can only return one column, we'll use a special marker
        # to indicate that this is a multi-column regex expansion
        if len(matched_columns) > 1:
            # Create a special column name that indicates multi-column expansion
            # The higher-level logic will need to handle this
            multi_col_name = "__REGEX_MULTI_COL__"
            # For now, return the first column but mark it specially
            quoted_col_name = matched_columns[0]
            snowpark_name = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    quoted_col_name
                )
            )
            col = get_col(snowpark_name)
            qualifiers = column_mapping.get_qualifier_for_spark_column(quoted_col_name)
            typed_col = TypedColumn(col, lambda: typer.type(col))
            typed_col.set_qualifiers(qualifiers)
            # Store matched columns info for later use
            typed_col._regex_matched_columns = matched_columns
            return (multi_col_name, typed_col)
        else:
            # Single column match - return that column
            quoted_col_name = matched_columns[0]
            snowpark_name = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    quoted_col_name
                )
            )
            col = get_col(snowpark_name)
            qualifiers = column_mapping.get_qualifier_for_spark_column(quoted_col_name)
            typed_col = TypedColumn(col, lambda: typer.type(col))
            typed_col.set_qualifiers(qualifiers)
            return (matched_columns[0], typed_col)

    quoted_attr_name = ".".join(
        quote_name_without_upper_casing(x) for x in name_parts[:-1]
    )
    if len(name_parts) > 1:
        quoted_attr_name = f"{quoted_attr_name}.{name_parts[-1]}"
    else:
        quoted_attr_name = name_parts[0]

    snowpark_name = column_mapping.get_snowpark_column_name_from_spark_column_name(
        quoted_attr_name, allow_non_exists=True
    )
    if snowpark_name is not None:
        col = get_col(snowpark_name)
        qualifiers = column_mapping.get_qualifier_for_spark_column(quoted_attr_name)
    else:
        # this means it has to be a struct column with a field name
        snowpark_name: str | None = None
        column_part_index: int = 0

        # Get catalog/database info from column map if available
        catalog_database_info = _get_catalog_database_from_column_map(
            original_attr_name, column_mapping
        )

        # Try to find the column name in different parts of the name_parts array
        # For qualified names like "table.column.field", we need to find the column part
        for i in range(len(name_parts)):
            candidate_column = name_parts[i]
            snowpark_name = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    candidate_column, allow_non_exists=True
                )
            )
            if snowpark_name is not None:
                column_part_index = i
                break

            # Also try in outer dataframes
            for outer_df in get_outer_dataframes():
                snowpark_name = (
                    outer_df.column_map.get_snowpark_column_name_from_spark_column_name(
                        candidate_column, allow_non_exists=True
                    )
                )
                if snowpark_name is not None:
                    column_part_index = i
                    break

            if snowpark_name is not None:
                break

        if snowpark_name is None:
            # Attempt LCA fallback.
            alias_tc = resolve_lca_alias(attr_name)

            if alias_tc is not None:
                # Return the TypedColumn that represents the alias.
                return (attr_name, alias_tc)

            # If qualified name not found, try to resolve as unqualified column name
            # This handles cases like "d.name" where we need to find "name" after a JOIN
            remaining_parts = name_parts
            if len(remaining_parts) > 1:
                unqualified_name = name_parts[-1]
                snowpark_name = (
                    column_mapping.get_snowpark_column_name_from_spark_column_name(
                        unqualified_name, allow_non_exists=True
                    )
                )
                if snowpark_name is not None:
                    col = get_col(snowpark_name)
                    qualifiers = column_mapping.get_qualifier_for_spark_column(
                        unqualified_name
                    )
                    typed_col = TypedColumn(col, lambda: typer.type(col))
                    typed_col.set_qualifiers(qualifiers)
                    # Store catalog/database info if found in column map
                    if catalog_database_info:
                        typed_col.set_catalog_database_info(catalog_database_info)
                    return (unqualified_name, typed_col)

        if snowpark_name is None:
            # Check if we're inside a lambda and trying to reference an outer column
            # This catches direct column references (not lambda variables)
            if is_lambda_being_resolved() and column_mapping:
                # Check if this column exists in the outer scope (not lambda params)
                outer_col_name = (
                    column_mapping.get_snowpark_column_name_from_spark_column_name(
                        attr_name, allow_non_exists=True
                    )
                )
                if outer_col_name:
                    # This is an outer scope column being referenced inside a lambda
                    raise AnalysisException(
                        f"Reference to non-lambda variable '{attr_name}' within lambda function. "
                        f"Lambda functions can only access their own parameters. "
                        f"If '{attr_name}' is a table column, it must be passed as an explicit parameter to the enclosing function."
                    )

            if has_plan_id:
                raise AnalysisException(
                    f'[RESOLVED_REFERENCE_COLUMN_NOT_FOUND] The column "{attr_name}" does not exist in the target dataframe.'
                )
            else:
                # Column does not exist. Pass in dummy column name for lazy error throwing as it could be a built-in function
                snowpark_name = attr_name

        col = get_col(snowpark_name)
        try:
            col_type = typer.type(col)[0]
        except SnowparkSQLException as e:
            if e.raw_message is not None and "invalid identifier" in e.raw_message:
                raise AnalysisException(
                    f'[COLUMN_NOT_FOUND] The column "{attr_name}" does not exist in the target dataframe.'
                )
            else:
                raise
        is_struct = isinstance(col_type, StructType)
        # for struct columns when accessed, spark use just the leaf field name rather than fully attributed one
        if is_struct:
            attr_name = name_parts[-1]

        # Calculate the field path correctly based on where we found the column
        path = name_parts[column_part_index + 1 :]
        if is_struct and not global_config.spark_sql_caseSensitive:
            path = _match_path_to_struct(path, col_type)

        for field_name in path:
            col = col.getItem(field_name)

        qualifiers = []

    typed_col = TypedColumn(col, lambda: typer.type(col))
    typed_col.set_qualifiers(qualifiers)

    # Store catalog/database info if available from column map
    final_catalog_database_info = _get_catalog_database_from_column_map(
        original_attr_name, column_mapping
    )
    if final_catalog_database_info:
        typed_col.set_catalog_database_info(final_catalog_database_info)

    return (name_parts[-1], typed_col)


def _match_path_to_struct(path: list[str], col_type: StructType) -> list[str]:
    """Takes a path of names and adjusts them to strictly match the field names in a StructType."""
    adjusted_path = []
    typ = col_type
    for i, name in enumerate(path):
        if isinstance(typ, StructType):
            lowercase_name = name.lower()
            for field in typ.fields:
                if field.name.lower() == lowercase_name:
                    adjusted_path.append(field.name)
                    typ = field.datatype
                    break
        elif isinstance(typ, MapType) or isinstance(typ, ArrayType):
            # For MapType and ArrayType, we can use the name as is.
            adjusted_path.append(name)
            typ = typ.value_type if isinstance(typ, MapType) else typ.element_type
        else:
            # If the type is not a struct, map, or array, we cannot access the field.
            raise AnalysisException(
                f"[INVALID_EXTRACT_BASE_FIELD_TYPE] Can't extract a value from \"{'.'.join(path[:i])}\". Need a complex type [STRUCT, ARRAY, MAP] but got \"{typ}\"."
            )
    return adjusted_path
