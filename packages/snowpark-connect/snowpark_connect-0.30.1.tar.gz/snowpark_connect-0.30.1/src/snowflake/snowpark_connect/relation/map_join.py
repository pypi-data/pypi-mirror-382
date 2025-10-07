#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from functools import reduce

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import JoinColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.constants import COLUMN_METADATA_COLLISION_KEY
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.error.error_utils import SparkException
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import JoinExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import (
    NATURAL_JOIN_TYPE_BASE,
    map_relation,
)
from snowflake.snowpark_connect.relation.read.metadata_utils import (
    filter_metadata_columns,
)
from snowflake.snowpark_connect.utils.context import (
    push_evaluating_join_condition,
    push_sql_scope,
    set_plan_id_map,
    set_sql_plan_name,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

USING_COLUMN_NOT_FOUND_ERROR = "[UNRESOLVED_USING_COLUMN_FOR_JOIN] USING column `{0}` not found on the {1} side of the join. The {1}-side columns: {2}"


def map_join(rel: relation_proto.Relation) -> DataFrameContainer:
    left_container: DataFrameContainer = map_relation(rel.join.left)
    right_container: DataFrameContainer = map_relation(rel.join.right)

    # Remove any metadata columns(like metada$filename) present in the dataframes.
    # We cannot support inputfilename for multisources as each dataframe has it's own source.
    left_container = filter_metadata_columns(left_container)
    right_container = filter_metadata_columns(right_container)

    left_input: snowpark.DataFrame = left_container.dataframe
    right_input: snowpark.DataFrame = right_container.dataframe
    is_natural_join = rel.join.join_type >= NATURAL_JOIN_TYPE_BASE
    using_columns = rel.join.using_columns
    if is_natural_join:
        rel.join.join_type -= NATURAL_JOIN_TYPE_BASE
        left_spark_columns = left_container.column_map.get_spark_columns()
        right_spark_columns = right_container.column_map.get_spark_columns()
        common_spark_columns = [
            x for x in left_spark_columns if x in right_spark_columns
        ]
        using_columns = common_spark_columns

    match rel.join.join_type:
        case relation_proto.Join.JOIN_TYPE_UNSPECIFIED:
            # TODO: Understand what UNSPECIFIED Join type is
            raise SnowparkConnectNotImplementedError("Unspecified Join Type")
        case relation_proto.Join.JOIN_TYPE_INNER:
            join_type = "inner"
        case relation_proto.Join.JOIN_TYPE_FULL_OUTER:
            join_type = "full_outer"
        case relation_proto.Join.JOIN_TYPE_LEFT_OUTER:
            join_type = "left"
        case relation_proto.Join.JOIN_TYPE_RIGHT_OUTER:
            join_type = "right"
        case relation_proto.Join.JOIN_TYPE_LEFT_ANTI:
            join_type = "leftanti"
        case relation_proto.Join.JOIN_TYPE_LEFT_SEMI:
            join_type = "leftsemi"
        case relation_proto.Join.JOIN_TYPE_CROSS:
            join_type = "cross"
        case other:
            raise SnowparkConnectNotImplementedError(f"Other Join Type: {other}")

    # This handles case sensitivity for using_columns
    case_corrected_right_columns: list[str] = []

    if rel.join.HasField("join_condition"):
        assert not using_columns

        left_columns = list(left_container.column_map.spark_to_col.keys())
        right_columns = list(right_container.column_map.spark_to_col.keys())

        # All PySpark join types are in the format of JOIN_TYPE_XXX.
        # We remove the first 10 characters (JOIN_TYPE_) and replace all underscores with spaces to match the exception.
        pyspark_join_type = relation_proto.Join.JoinType.Name(rel.join.join_type)[
            10:
        ].replace("_", " ")
        with push_sql_scope(), push_evaluating_join_condition(
            pyspark_join_type, left_columns, right_columns
        ):
            if left_container.alias is not None:
                set_sql_plan_name(left_container.alias, rel.join.left.common.plan_id)
            if right_container.alias is not None:
                set_sql_plan_name(right_container.alias, rel.join.right.common.plan_id)
            _, join_expression = map_single_column_expression(
                rel.join.join_condition,
                column_mapping=JoinColumnNameMap(
                    left_container.column_map,
                    right_container.column_map,
                ),
                typer=JoinExpressionTyper(left_input, right_input),
            )
        result: snowpark.DataFrame = left_input.join(
            right=right_input,
            on=join_expression.col,
            how=join_type,
            lsuffix="_left",
            rsuffix="_right",
        )
    elif using_columns:
        if any(
            left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                c, allow_non_exists=True, return_first=True
            )
            is None
            for c in using_columns
        ):
            import pyspark

            raise pyspark.errors.AnalysisException(
                USING_COLUMN_NOT_FOUND_ERROR.format(
                    next(
                        c
                        for c in using_columns
                        if left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                            c, allow_non_exists=True, return_first=True
                        )
                        is None
                    ),
                    "left",
                    left_container.column_map.get_spark_columns(),
                )
            )
        if any(
            right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                c, allow_non_exists=True, return_first=True
            )
            is None
            for c in using_columns
        ):
            import pyspark

            raise pyspark.errors.AnalysisException(
                USING_COLUMN_NOT_FOUND_ERROR.format(
                    next(
                        c
                        for c in using_columns
                        if right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                            c, allow_non_exists=True, return_first=True
                        )
                        is None
                    ),
                    "right",
                    right_container.column_map.get_spark_columns(),
                )
            )

        # Round trip the using columns through the column map to get the correct names
        # in order to support case sensitivity.
        # TODO: case_corrected_left_columns / case_corrected_right_columns may no longer be required as Snowpark dataframe preserves the column casing now.
        case_corrected_left_columns = left_container.column_map.get_spark_column_names_from_snowpark_column_names(
            left_container.column_map.get_snowpark_column_names_from_spark_column_names(
                list(using_columns), return_first=True
            )
        )
        case_corrected_right_columns = right_container.column_map.get_spark_column_names_from_snowpark_column_names(
            right_container.column_map.get_snowpark_column_names_from_spark_column_names(
                list(using_columns), return_first=True
            )
        )
        using_columns = zip(case_corrected_left_columns, case_corrected_right_columns)
        # We cannot assume that Snowpark will have the same names for left and right columns,
        # so we convert ["a", "b"] into (left["a"] == right["a"] & left["b"] == right["b"]),
        # then drop right["a"] and right["b"].
        snowpark_using_columns = [
            (
                left_input[
                    left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        lft, return_first=True
                    )
                ],
                right_input[
                    right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        r, return_first=True
                    )
                ],
            )
            for lft, r in using_columns
        ]
        joined_df = left_input.join(
            right=right_input,
            on=reduce(
                snowpark.Column.__and__,
                (left == right for left, right in snowpark_using_columns),
            ),
            how=join_type,
        )
        # For outer joins, we need to preserve join keys from both sides using COALESCE
        if join_type == "full_outer":
            coalesced_columns = []
            columns_to_drop = []
            for i, (left_col, right_col) in enumerate(snowpark_using_columns):
                # Use the original user-specified column name to preserve case sensitivity
                original_column_name = rel.join.using_columns[i]
                coalesced_col = snowpark_fn.coalesce(left_col, right_col).alias(
                    original_column_name
                )
                coalesced_columns.append(coalesced_col)
                columns_to_drop.extend([left_col, right_col])

            other_columns = [
                snowpark_fn.col(col_name)
                for col_name in joined_df.columns
                if col_name not in [col.getName() for col in columns_to_drop]
            ]
            result = joined_df.select(coalesced_columns + other_columns)
        else:
            result = joined_df.drop(*(right for _, right in snowpark_using_columns))
    else:
        if join_type != "cross" and not global_config.spark_sql_crossJoin_enabled:
            raise SparkException.implicit_cartesian_product("inner")
        result: snowpark.DataFrame = left_input.join(
            right=right_input,
            how=join_type,
        )

    if join_type in ["leftanti", "leftsemi"]:
        # Join types that only return columns from the left side:
        # - LEFT SEMI JOIN: Returns left rows that have matches in right table (no right columns)
        # - LEFT ANTI JOIN: Returns left rows that have NO matches in right table (no right columns)
        # Both preserve only the columns from the left DataFrame without adding any columns from the right.
        spark_cols_after_join: list[str] = left_container.column_map.get_spark_columns()
        qualifiers = left_container.column_map.get_qualifiers()
    else:
        # Add Spark columns and plan_ids from left DF
        spark_cols_after_join: list[str] = list(
            left_container.column_map.get_spark_columns()
        ) + [
            spark_col
            for i, spark_col in enumerate(
                right_container.column_map.get_spark_columns()
            )
            if spark_col not in case_corrected_right_columns
            or spark_col
            in right_container.column_map.get_spark_columns()[
                :i
            ]  # this is to make sure we only remove the column once
        ]

        qualifiers = list(left_container.column_map.get_qualifiers()) + [
            right_container.column_map.get_qualifier_for_spark_column(spark_col)
            for i, spark_col in enumerate(
                right_container.column_map.get_spark_columns()
            )
            if spark_col not in case_corrected_right_columns
            or spark_col
            in right_container.column_map.get_spark_columns()[
                :i
            ]  # this is to make sure we only remove the column once]
        ]

    column_metadata = {}
    if left_container.column_map.column_metadata:
        column_metadata.update(left_container.column_map.column_metadata)

    if right_container.column_map.column_metadata:
        for key, value in right_container.column_map.column_metadata.items():
            if key not in column_metadata:
                column_metadata[key] = value
            else:
                # In case of collision, use snowpark's column's expr_id as prefix.
                # this is a temporary solution until SNOW-1926440 is resolved.
                try:
                    snowpark_name = right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        key
                    )
                    expr_id = right_input[snowpark_name]._expression.expr_id
                    updated_key = COLUMN_METADATA_COLLISION_KEY.format(
                        expr_id=expr_id, key=snowpark_name
                    )
                    column_metadata[updated_key] = value
                except Exception:
                    # ignore any errors that happens while fetching the metadata
                    pass

    result_container = DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=spark_cols_after_join,
        snowpark_column_names=result.columns,
        column_metadata=column_metadata,
        column_qualifiers=qualifiers,
    )

    # Fix for USING join column references with different plan IDs
    # After a USING join, references to the right dataframe's columns should resolve
    # to the result dataframe that contains the merged columns
    if (
        using_columns
        and rel.join.right.HasField("common")
        and rel.join.right.common.HasField("plan_id")
    ):
        right_plan_id = rel.join.right.common.plan_id
        set_plan_id_map(right_plan_id, result_container)

    # For FULL OUTER joins, we also need to map the left dataframe's plan_id
    # since both columns are replaced with a coalesced column
    if (
        using_columns
        and join_type == "full_outer"
        and rel.join.left.HasField("common")
        and rel.join.left.common.HasField("plan_id")
    ):
        left_plan_id = rel.join.left.common.plan_id
        set_plan_id_map(left_plan_id, result_container)

    if rel.join.using_columns:
        # When join 'using_columns', the 'join columns' should go first in result DF.
        idxs_to_shift = [
            spark_cols_after_join.index(left_col_name)
            for left_col_name in case_corrected_left_columns
        ]

        def reorder(lst: list) -> list:
            to_move = [lst[i] for i in idxs_to_shift]
            remaining = [el for i, el in enumerate(lst) if i not in idxs_to_shift]
            return to_move + remaining

        # Create reordered DataFrame
        reordered_df = result_container.dataframe.select(
            [snowpark_fn.col(c) for c in reorder(result_container.dataframe.columns)]
        )

        # Create new container with reordered metadata
        original_df = result_container.dataframe
        return DataFrameContainer.create_with_column_mapping(
            dataframe=reordered_df,
            spark_column_names=reorder(result_container.column_map.get_spark_columns()),
            snowpark_column_names=reorder(
                result_container.column_map.get_snowpark_columns()
            ),
            column_metadata=column_metadata,
            column_qualifiers=reorder(qualifiers),
            table_name=result_container.table_name,
            cached_schema_getter=lambda: snowpark.types.StructType(
                reorder(original_df.schema.fields)
            ),
        )

    return result_container
