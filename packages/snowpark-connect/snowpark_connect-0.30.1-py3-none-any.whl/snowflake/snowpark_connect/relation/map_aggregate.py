#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import re
from dataclasses import dataclass
from typing import Optional

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark import Column
from snowflake.snowpark._internal.analyzer.unary_expression import Alias
from snowflake.snowpark.types import DataType
from snowflake.snowpark_connect.column_name_handler import (
    make_column_names_snowpark_compatible,
)
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.expression.literal import get_literal_field_and_name
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    get_is_evaluating_sql,
    set_current_grouping_columns,
    temporary_pivot_expression,
)


def map_group_by_aggregate(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Groups the DataFrame using the specified columns.

    Aggregations come in as expressions, which are mapped to `snowpark.Column`
    objects.
    """
    input_df_container, columns = map_aggregate_helper(rel)
    input_df_actual = input_df_container.dataframe

    if len(columns.grouping_expressions()) == 0:
        result = input_df_actual.agg(*columns.aggregation_expressions())
    else:
        result = input_df_actual.group_by(*columns.grouping_expressions()).agg(
            *columns.aggregation_expressions()
        )
    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=columns.spark_names(),
        snowpark_column_names=columns.snowpark_names(),
        snowpark_column_types=columns.data_types(),
        column_qualifiers=columns.get_qualifiers(),
        parent_column_name_map=input_df_container.column_map,
    )


def map_rollup_aggregate(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Create a multidimensional rollup for the current DataFrame using the specified columns.

    Aggregations come in as expressions, which are mapped to `snowpark.Column`
    objects.
    """
    input_container, columns = map_aggregate_helper(rel)
    input_df_actual = input_container.dataframe

    if len(columns.grouping_expressions()) == 0:
        result = input_df_actual.agg(*columns.aggregation_expressions())
    else:
        result = input_df_actual.rollup(*columns.grouping_expressions()).agg(
            *columns.aggregation_expressions()
        )
    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=columns.spark_names(),
        snowpark_column_names=columns.snowpark_names(),
        snowpark_column_types=columns.data_types(),
        column_qualifiers=columns.get_qualifiers(),
        parent_column_name_map=input_container.column_map,
    )


def map_cube_aggregate(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Create a multidimensional cube for the current DataFrame using the specified columns.

    Aggregations come in as expressions, which are mapped to `snowpark.Column`
    objects.
    """
    input_container, columns = map_aggregate_helper(rel)
    input_df_actual = input_container.dataframe

    if len(columns.grouping_expressions()) == 0:
        result = input_df_actual.agg(*columns.aggregation_expressions())
    else:
        result = input_df_actual.cube(*columns.grouping_expressions()).agg(
            *columns.aggregation_expressions()
        )
    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=columns.spark_names(),
        snowpark_column_names=columns.snowpark_names(),
        snowpark_column_types=columns.data_types(),
        column_qualifiers=columns.get_qualifiers(),
        parent_column_name_map=input_container.column_map,
    )


def map_pivot_aggregate(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Pivots a column of the current DataFrame and performs the specified aggregation.

    There are 2 versions of the pivot function: one that requires the caller to specify the list of the distinct values
    to pivot on and one that does not.
    """
    input_container, columns = map_aggregate_helper(rel, pivot=True, skip_alias=True)
    input_df_actual = input_container.dataframe

    pivot_column = map_single_column_expression(
        rel.aggregate.pivot.col,
        input_container.column_map,
        ExpressionTyper(input_df_actual),
    )
    pivot_values = [
        get_literal_field_and_name(lit)[0] for lit in rel.aggregate.pivot.values
    ]

    used_columns = {pivot_column[1].col._expression.name}
    if get_is_evaluating_sql():
        # When evaluating SQL spark doesn't trim columns from the result
        used_columns = {"*"}
    else:
        for expression in rel.aggregate.aggregate_expressions:
            matched_identifiers = re.findall(
                r'unparsed_identifier: "(.*)"', expression.__str__()
            )
            for identifier in matched_identifiers:
                mapped_col = input_container.column_map.spark_to_col.get(
                    identifier, None
                )
                if mapped_col:
                    used_columns.add(mapped_col[0].snowpark_name)

    if len(columns.grouping_expressions()) == 0:
        # Snowpark doesn't support multiple aggregations in pivot without groupBy
        # So we need to perform each aggregation separately and then combine results
        if len(columns.aggregation_expressions(unalias=True)) > 1:
            agg_expressions = columns.aggregation_expressions(unalias=True)
            agg_metadata = columns.aggregation_columns
            num_agg_functions = len(agg_expressions)

            spark_names = []
            pivot_results = []
            for i, agg_expr in enumerate(agg_expressions):
                pivot_result = (
                    input_df_actual.select(*used_columns)
                    .pivot(pivot_column[1].col, pivot_values if pivot_values else None)
                    .agg(agg_expr)
                )
                for col_name in pivot_result.columns:
                    spark_names.append(
                        f"{pivot_column_name(col_name)}_{agg_metadata[i].spark_name}"
                    )
                pivot_results.append(pivot_result)

            result = pivot_results[0]
            for pivot_result in pivot_results[1:]:
                result = result.cross_join(pivot_result)

            pivot_columns_per_agg = len(pivot_results[0].columns)
            reordered_spark_names = []
            reordered_snowpark_names = []
            reordered_types = []
            column_selectors = []

            for pivot_idx in range(pivot_columns_per_agg):
                for agg_idx in range(num_agg_functions):
                    current_pos = agg_idx * pivot_columns_per_agg + pivot_idx
                    if current_pos < len(spark_names):
                        idx = current_pos + 1  # 1-based indexing for Snowpark
                        reordered_spark_names.append(spark_names[current_pos])
                        reordered_snowpark_names.append(f"${idx}")
                        reordered_types.append(
                            result.schema.fields[current_pos].datatype
                        )
                        column_selectors.append(snowpark_fn.col(f"${idx}"))

            return DataFrameContainer.create_with_column_mapping(
                dataframe=result.select(*column_selectors),
                spark_column_names=reordered_spark_names,
                snowpark_column_names=reordered_snowpark_names,
                column_qualifiers=[[]] * len(reordered_spark_names),
                parent_column_name_map=input_container.column_map,
                snowpark_column_types=reordered_types,
            )
        else:
            result = (
                input_df_actual.select(*used_columns)
                .pivot(pivot_column[1].col, pivot_values if pivot_values else None)
                .agg(*columns.aggregation_expressions(unalias=True))
            )
    else:
        result = (
            input_df_actual.group_by(*columns.grouping_expressions())
            .pivot(pivot_column[1].col, pivot_values if pivot_values else None)
            .agg(*columns.aggregation_expressions(unalias=True))
        )

    agg_name_list = [c.spark_name for c in columns.grouping_columns]

    # Calculate number of pivot values for proper Spark-compatible indexing
    total_pivot_columns = len(result.columns) - len(agg_name_list)
    num_pivot_values = (
        total_pivot_columns // len(columns.aggregation_columns)
        if len(columns.aggregation_columns) > 0
        else 1
    )

    def _get_agg_exp_alias_for_col(col_index: int) -> Optional[str]:
        if col_index < len(agg_name_list) or len(columns.aggregation_columns) <= 1:
            return None
        else:
            index = (col_index - len(agg_name_list)) // num_pivot_values
            return columns.aggregation_columns[index].spark_name

    spark_columns = []
    for col in [
        pivot_column_name(c, _get_agg_exp_alias_for_col(i))
        for i, c in enumerate(result.columns)
    ]:
        spark_col = (
            input_container.column_map.get_spark_column_name_from_snowpark_column_name(
                col, allow_non_exists=True
            )
        )

        if spark_col is not None:
            spark_columns.append(spark_col)
        else:
            # Handle NULL column names to match Spark behavior (lowercase 'null')
            if col == "NULL":
                spark_columns.append(col.lower())
            else:
                spark_columns.append(col)

    grouping_cols_count = len(agg_name_list)
    pivot_cols = result.columns[grouping_cols_count:]
    spark_pivot_cols = spark_columns[grouping_cols_count:]

    num_agg_functions = len(columns.aggregation_columns)
    num_pivot_values = len(pivot_cols) // num_agg_functions

    reordered_snowpark_cols = []
    reordered_spark_cols = []
    column_indices = []  # 1-based indexing

    for i in range(grouping_cols_count):
        reordered_snowpark_cols.append(result.columns[i])
        reordered_spark_cols.append(spark_columns[i])
        column_indices.append(i + 1)

    for pivot_idx in range(num_pivot_values):
        for agg_idx in range(num_agg_functions):
            current_pos = agg_idx * num_pivot_values + pivot_idx
            if current_pos < len(pivot_cols):
                reordered_snowpark_cols.append(pivot_cols[current_pos])
                reordered_spark_cols.append(spark_pivot_cols[current_pos])
                original_index = grouping_cols_count + current_pos
                column_indices.append(original_index + 1)

    reordered_result = result.select(
        *[snowpark_fn.col(f"${idx}") for idx in column_indices]
    )

    return DataFrameContainer.create_with_column_mapping(
        dataframe=reordered_result,
        spark_column_names=reordered_spark_cols,
        snowpark_column_names=[f"${idx}" for idx in column_indices],
        column_qualifiers=(
            columns.get_qualifiers()[: len(agg_name_list)]
            + [[]] * (len(reordered_spark_cols) - len(agg_name_list))
        ),
        parent_column_name_map=input_container.column_map,
        snowpark_column_types=[
            result.schema.fields[idx - 1].datatype for idx in column_indices
        ],
    )


def pivot_column_name(snowpark_cname, opt_alias: Optional[str] = None) -> Optional[str]:
    # For values that are used as pivoted columns, the input and output are in the following format (outermost double quotes are part of the input):

    # 1. "'Java'" -> Java
    # 2. "'""C++""'" -> "C++"
    # 3. "'""""''Scala''""""'" -> ""'Scala'""

    # As we can see:
    # 1. the whole content is always nested in a double quote followed by a single quote ("'<content>'").
    # 2. the string content is nested in single quotes ('<string_content>')
    # 3. double quote is escased by another double quote, this is snowflake behavior
    # 4. if there is a single quote followed by a single quote, the first single quote needs to be preserved in the output

    try:
        # handling values that are used as pivoted columns
        match = re.match(r'^"\'(.*)\'"$', snowpark_cname)
        # extract the content between the outermost double quote followed by a single quote "'
        content = match.group(1)
        # convert the escaped double quote to the actual double quote
        content = content.replace('""', '"')
        escape_single_quote_placeholder = "__SAS_PLACEHOLDER_ESCAPE_SINGLE_QUOTE__"
        # replace two consecutive single quote in the content with a placeholder, the first single quote needs to be preserved
        content = re.sub(r"''", escape_single_quote_placeholder, content)
        # remove the solo single quote, they are not part of the string content
        content = re.sub(r"'", "", content)
        # replace the placeholder with the single quote which we want to preserve
        result = content.replace(escape_single_quote_placeholder, "'")
        return f"{result}_{opt_alias}" if opt_alias else result
    except Exception:
        # fallback to the original logic, handling aliased column names
        double_quote_list = re.findall(r'"(.*?)"', snowpark_cname)
        spark_string = ""
        for entry in list(filter(None, double_quote_list)):
            if "'" in entry:
                entry = entry.replace("'", "")
                if len(entry) > 0:
                    spark_string += entry
            elif entry.isdigit() or re.compile(r"^\d+?\.\d+?$").match(entry):
                # skip quoting digits or decimal numbers as column names.
                spark_string += entry
            else:
                spark_string += '"' + entry + '"'
        return snowpark_cname if spark_string == "" else spark_string


@dataclass(frozen=True)
class _ColumnMetadata:
    expression: snowpark.Column
    spark_name: str
    snowpark_name: str
    data_type: DataType
    qualifiers: list[str]


@dataclass(frozen=True)
class _Columns:
    grouping_columns: list[_ColumnMetadata]
    aggregation_columns: list[_ColumnMetadata]
    can_infer_schema: bool

    def grouping_expressions(self) -> list[snowpark.Column]:
        return [col.expression for col in self.grouping_columns]

    def aggregation_expressions(self, unalias: bool = False) -> list[snowpark.Column]:
        def _unalias(col: snowpark.Column) -> snowpark.Column:
            if unalias and hasattr(col, "_expr1") and isinstance(col._expr1, Alias):
                return _unalias(Column(col._expr1.child))
            else:
                return col

        return [_unalias(col.expression) for col in self.aggregation_columns]

    def expressions(self) -> list[snowpark.Column]:
        return self.grouping_expressions() + self.aggregation_expressions()

    def snowpark_names(self) -> list[str]:
        return [
            col.snowpark_name
            for col in self.grouping_columns + self.aggregation_columns
            if col.snowpark_name is not None
        ]

    def spark_names(self) -> list[str]:
        return [
            col.spark_name for col in self.grouping_columns + self.aggregation_columns
        ]

    def get_qualifiers(self) -> list[list[str]]:
        return [
            col.qualifiers for col in self.grouping_columns + self.aggregation_columns
        ]

    def data_types(self) -> list[DataType] | None:
        if not self.can_infer_schema:
            return None
        return [
            col.data_type
            for col in self.grouping_columns + self.aggregation_columns
            if col.data_type is not None
        ]


def map_aggregate_helper(
    rel: relation_proto.Relation, pivot: bool = False, skip_alias: bool = False
):
    input_container = map_relation(rel.aggregate.input)
    input_df = input_container.dataframe
    grouping_expressions = rel.aggregate.grouping_expressions
    expressions = rel.aggregate.aggregate_expressions
    groupings: list[_ColumnMetadata] = []
    aggregations: list[_ColumnMetadata] = []

    typer = ExpressionTyper(input_df)
    schema_inferrable = True

    with temporary_pivot_expression(pivot):
        for exp in grouping_expressions:
            new_name, snowpark_column = map_single_column_expression(
                exp, input_container.column_map, typer
            )
            alias = make_column_names_snowpark_compatible(
                [new_name], rel.common.plan_id, len(groupings)
            )[0]
            groupings.append(
                _ColumnMetadata(
                    snowpark_column.col
                    if skip_alias
                    else snowpark_column.col.alias(alias),
                    new_name,
                    None if skip_alias else alias,
                    None if pivot else snowpark_column.typ,
                    snowpark_column.get_qualifiers(),
                )
            )

        grouping_cols = [g.spark_name for g in groupings]
        set_current_grouping_columns(grouping_cols)

        for exp in expressions:
            new_name, snowpark_column = map_single_column_expression(
                exp, input_container.column_map, typer
            )
            alias = make_column_names_snowpark_compatible(
                [new_name], rel.common.plan_id, len(groupings) + len(aggregations)
            )[0]

            def type_agg_expr(
                agg_exp: TypedColumn, schema_inferrable: bool
            ) -> DataType | None:
                if pivot or not schema_inferrable:
                    return None
                try:
                    return agg_exp.typ
                except Exception:
                    # This type used for schema inference optimization purposes.
                    # typer may not be able to infer the type of some expressions
                    # in that case we return None, and the optimization will not be applied.
                    return None

            agg_col_typ = type_agg_expr(snowpark_column, schema_inferrable)
            if agg_col_typ is None:
                schema_inferrable = False

            aggregations.append(
                _ColumnMetadata(
                    snowpark_column.col
                    if skip_alias
                    else snowpark_column.col.alias(alias),
                    new_name,
                    None if skip_alias else alias,
                    agg_col_typ,
                    [],
                )
            )

        return (
            input_container,
            _Columns(
                grouping_columns=groupings,
                aggregation_columns=aggregations,
                can_infer_schema=schema_inferrable,
            ),
        )
