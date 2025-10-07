#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
from pyspark.errors.exceptions.base import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
)
from snowflake.snowpark.types import StructType
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import get_outer_dataframes
from snowflake.snowpark_connect.utils.identifiers import (
    split_fully_qualified_spark_name,
)


def check_struct_and_get_field_datatype(field_name, schema):
    if isinstance(schema, StructType):
        if field_name in schema.names:
            return schema.__getitem__(field_name).datatype
        else:
            return None
    else:
        None


def map_unresolved_star(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[list[str], TypedColumn]:
    if exp.unresolved_star.HasField("unparsed_target"):
        unparsed_target = exp.unresolved_star.unparsed_target
        name_parts = split_fully_qualified_spark_name(unparsed_target)

        assert (
            len(name_parts) > 1 and name_parts[-1] == "*"
        ), f"Unable to parse unparsed_target {unparsed_target}"

        # scenario where it is expanding * to the current dataframe
        if len(name_parts) == 1:
            result_exp = snowpark_fn.sql_expr(
                ", ".join(column_mapping.get_snowpark_columns())
            )
            spark_names = column_mapping.get_spark_columns()
            typed_column = TypedColumn(result_exp, lambda: typer.type(result_exp))
            typed_column.set_multi_col_qualifiers(column_mapping.get_qualifiers())
            return spark_names, typed_column

        # scenario where it is expanding * to mulitple columns
        spark_names = []
        snowpark_names = []
        qualifiers = []

        (
            spark_names,
            snowpark_names,
            qualifiers,
        ) = column_mapping.get_spark_and_snowpark_columns_with_qualifier_for_qualifier(
            name_parts[:-1]
        )

        if len(spark_names) == 0:
            for outer_df_container in get_outer_dataframes():
                column_mapping_for_outer_df = outer_df_container.column_map
                (
                    spark_names,
                    snowpark_names,
                    qualifiers,
                ) = column_mapping_for_outer_df.get_spark_and_snowpark_columns_with_qualifier_for_qualifier(
                    name_parts[:-1]
                )
                if len(spark_names) > 0:
                    break

        if len(spark_names) > 0:
            final_sql_expr = snowpark_fn.sql_expr(", ".join(snowpark_names))
            typed_column = TypedColumn(
                final_sql_expr, lambda: typer.type(final_sql_expr)
            )
            typed_column.set_multi_col_qualifiers(qualifiers)
            return spark_names, typed_column

        # scenario where it is expanding * to a struct field
        # any prefix can be the column name and the rest can be the struct field names
        # we will loop over all the possiblities
        # it should be in form of alis_1.alias_2.column_name.field_1.field_2.*
        # prefix will be name[:i], column would be name[i] and fields would be name[i + 1 : -1] and name[-1] should be "*"
        # column itself can be a struct column in which case prefix will be empty
        for i in range(0, len(name_parts) - 1):
            if i == 0:
                prefix_candidate_str = name_parts[i]
            else:
                prefix_candidate_str = ".".join(
                    quote_name_without_upper_casing(x) for x in name_parts[:i]
                )
                prefix_candidate_str = f"{prefix_candidate_str}.{name_parts[i]}"
            prefix_candidate = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    prefix_candidate_str, allow_non_exists=True
                )
            )
            if prefix_candidate is None:
                for outer_df_container in get_outer_dataframes():
                    prefix_candidate = outer_df_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        prefix_candidate_str, allow_non_exists=True
                    )
                    if prefix_candidate is not None:
                        break

            if prefix_candidate is not None:
                candidate_leaf_field = typer.df.schema
                fields = [prefix_candidate] + name_parts[i + 1 : -1]
                for subfield in fields:
                    if (
                        candidate_leaf_field := check_struct_and_get_field_datatype(
                            subfield, candidate_leaf_field
                        )
                    ) is None:
                        prefix_candidate = None
                        break

                if prefix_candidate is None:
                    continue

                spark_names = candidate_leaf_field.names
                prefix_candidate = ":".join(fields)
                all_snowpark_names = [
                    f"{prefix_candidate}:{spark_name}" for spark_name in spark_names
                ]
                final_sql_expr = snowpark_fn.sql_expr(", ".join(all_snowpark_names))

                typed_column = TypedColumn(
                    final_sql_expr,
                    lambda final_sql_expr=final_sql_expr: typer.type(final_sql_expr),
                )
                typed_column.set_multi_col_qualifiers([[] for _ in spark_names])
                return spark_names, typed_column
    else:
        result_exp = snowpark_fn.sql_expr(
            ", ".join(column_mapping.get_snowpark_columns())
        )
        spark_names = column_mapping.get_spark_columns()
        typed_column = TypedColumn(
            result_exp, lambda: [f.datatype for f in typer.df.schema]
        )
        typed_column.set_multi_col_qualifiers(column_mapping.get_qualifiers())
        return spark_names, typed_column

    raise AnalysisException(
        f"[UNRESOLVED_STAR] The unresolved star expression {exp} is not supported."
    )


def map_unresolved_star_struct(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[list[str], list]:
    unparsed_target = exp.unresolved_star.unparsed_target
    name_parts = split_fully_qualified_spark_name(unparsed_target)

    assert (
        len(name_parts) > 1 and name_parts[-1] == "*"
    ), f"Unable to parse unparsed_target {unparsed_target}"

    expanded_args = []
    for i in range(0, len(name_parts) - 1):
        if i == 0:
            prefix_candidate_str = name_parts[i]
        else:
            prefix_candidate_str = ".".join(
                quote_name_without_upper_casing(x) for x in name_parts[:i]
            )
            prefix_candidate_str = f"{prefix_candidate_str}.{name_parts[i]}"
        prefix_candidate = (
            column_mapping.get_snowpark_column_name_from_spark_column_name(
                prefix_candidate_str, allow_non_exists=True
            )
        )
        if prefix_candidate is None:
            for outer_df_container in get_outer_dataframes():
                prefix_candidate = outer_df_container.column_map.get_snowpark_column_name_from_spark_column_name(
                    prefix_candidate_str, allow_non_exists=True
                )
                if prefix_candidate is not None:
                    break

        if prefix_candidate is not None:
            candidate_leaf_field = typer.df.schema
            fields = [prefix_candidate] + name_parts[i + 1 : -1]
            for subfield in fields:
                if (
                    candidate_leaf_field := check_struct_and_get_field_datatype(
                        subfield, candidate_leaf_field
                    )
                ) is None:
                    prefix_candidate = None
                    break

            if prefix_candidate is None:
                continue

            spark_names = candidate_leaf_field.names
            prefix_candidate = ":".join(fields)

            for spark_name in spark_names:
                expanded_args.append(snowpark_fn.lit(spark_name))
                field_snowpark_name = f"{prefix_candidate}:{spark_name}"
                field_col = snowpark_fn.sql_expr(field_snowpark_name)
                expanded_args.append(field_col)

    return spark_names, expanded_args
