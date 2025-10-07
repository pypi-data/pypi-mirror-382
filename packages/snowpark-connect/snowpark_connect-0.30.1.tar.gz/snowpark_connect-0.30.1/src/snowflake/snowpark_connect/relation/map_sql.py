#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import re
from collections.abc import MutableMapping, MutableSequence
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from functools import reduce
from typing import Tuple

import jpype
import pandas
import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
import pyspark.sql.connect.proto.relations_pb2 as relation_proto
import sqlglot
from google.protobuf.any_pb2 import Any
from pyspark.errors.exceptions.base import (
    AnalysisException,
    UnsupportedOperationException,
)
from sqlglot.expressions import ColumnDef, DataType, FileFormatProperty, Identifier

import snowflake.snowpark.functions as snowpark_fn
import snowflake.snowpark_connect.proto.snowflake_expression_ext_pb2 as snowflake_exp_proto
import snowflake.snowpark_connect.proto.snowflake_relation_ext_pb2 as snowflake_proto
from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
    unquote_if_quoted,
)
from snowflake.snowpark._internal.type_utils import convert_sp_to_sf_type
from snowflake.snowpark._internal.utils import is_sql_select_statement, quote_name
from snowflake.snowpark.functions import when_matched, when_not_matched
from snowflake.snowpark_connect.client import (
    SQL_PASS_THROUGH_MARKER,
    calculate_checksum,
)
from snowflake.snowpark_connect.config import (
    auto_uppercase_non_column_identifiers,
    check_table_supports_operation,
    get_boolean_session_config_param,
    global_config,
    record_table_metadata,
    set_config_param,
    unset_config_param,
)
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.expression.map_expression import (
    ColumnNameMap,
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.relation.catalogs.utils import (
    CURRENT_CATALOG_NAME,
    _get_current_temp_objects,
)
from snowflake.snowpark_connect.relation.map_relation import (
    NATURAL_JOIN_TYPE_BASE,
    map_relation,
)
from snowflake.snowpark_connect.type_mapping import map_snowpark_to_pyspark_types
from snowflake.snowpark_connect.utils.context import (
    _accessing_temp_object,
    gen_sql_plan_id,
    get_session_id,
    get_sql_plan,
    push_evaluating_sql_scope,
    push_processed_view,
    push_sql_scope,
    set_plan_id_map,
    set_sql_args,
    set_sql_plan_name,
)
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
    telemetry,
)

from .. import column_name_handler
from ..expression.map_sql_expression import (
    _window_specs,
    as_java_list,
    as_java_map,
    map_logical_plan_expression,
    sql_parser,
)
from ..utils.identifiers import (
    spark_to_sf_single_id,
    spark_to_sf_single_id_with_unquoting,
)
from ..utils.temporary_view_cache import (
    get_temp_view,
    register_temp_view,
    unregister_temp_view,
)
from .catalogs import SNOWFLAKE_CATALOG

_ctes = ContextVar[dict[str, relation_proto.Relation]]("_ctes", default={})
_cte_definitions = ContextVar[dict[str, any]]("_cte_definitions", default={})
_having_condition = ContextVar[expressions_proto.Expression | None](
    "_having_condition", default=None
)


def _is_sql_select_statement_helper(sql_string: str) -> bool:
    """
    Determine if a SQL string is a SELECT or CTE query statement, even when it starts with comments or whitespace.
    """
    if not sql_string:
        return False

    trimmed = sql_string.lstrip()

    while trimmed:
        if trimmed.startswith("--"):
            newline_pos = trimmed.find("\n")
            if newline_pos == -1:
                return False
            trimmed = trimmed[newline_pos + 1 :].lstrip()
            continue
        elif trimmed.startswith("/*"):
            end_pos = trimmed.find("*/")
            if end_pos == -1:
                return False
            trimmed = trimmed[end_pos + 2 :].lstrip()
            continue
        break

    if not trimmed:
        return False

    return is_sql_select_statement(trimmed)


@contextmanager
def _push_cte_scope():
    """
    Creates a new CTE scope when evaluating nested WITH clauses.
    """
    cur_ctes = _ctes.get()
    cur_definitions = _cte_definitions.get()
    cte_token = _ctes.set(cur_ctes.copy())
    def_token = _cte_definitions.set(cur_definitions.copy())
    try:
        yield
    finally:
        _ctes.reset(cte_token)
        _cte_definitions.reset(def_token)


@contextmanager
def _push_window_specs_scope():
    """
    Creates a new window specs  scope when evaluating nested  clauses.
    """
    cur = _window_specs.get()
    token = _window_specs.set(cur.copy())
    try:
        yield
    finally:
        _window_specs.reset(token)


def _find_pos_args(node, positions: list[int]):
    if str(node.nodeName()) == "PosParameter":
        positions.append(node.pos())
    else:
        for child in as_java_list(node.children()):
            _find_pos_args(child, positions)
        if hasattr(node, "expressions"):
            for child in as_java_list(node.expressions()):
                _find_pos_args(child, positions)


def parse_pos_args(
    logical_plan,
    pos_args: MutableSequence[expressions_proto.Expression.Literal],
) -> dict[int, expressions_proto.Expression]:
    # Spark Connect gives us positional parameters as a regular list,
    # while Spark parser refers to them by their character indexes in the query.
    # Therefore, we need to find all positional parameters, sort their locations,
    # and match them to the list from Spark Connect.
    if not pos_args:
        return {}

    positions: list[int] = []
    _find_pos_args(logical_plan, positions)
    return dict(zip(sorted(positions), pos_args))


def execute_logical_plan(logical_plan) -> DataFrameContainer:
    proto = map_logical_plan_relation(logical_plan)
    telemetry.report_parsed_sql_plan(proto)
    with push_evaluating_sql_scope():
        return map_relation(proto)


def _spark_to_snowflake(multipart_id: jpype.JObject) -> str:
    return ".".join(
        spark_to_sf_single_id(str(part)) for part in as_java_list(multipart_id)
    )


def _rename_columns(
    df: snowpark.DataFrame, user_specified_columns, column_map: ColumnNameMap
) -> snowpark.DataFrame:
    user_columns = [str(col._1()) for col in as_java_list(user_specified_columns)]

    if user_columns:
        columns = zip(df.columns, user_columns)
    else:
        columns = column_map.snowpark_to_spark_map().items()

    for orig_column, user_column in columns:
        df = df.with_column_renamed(
            orig_column, spark_to_sf_single_id(user_column, is_column=True)
        )
    return df


def _create_table_as_select(logical_plan, mode: str) -> None:
    # TODO: for as select create tables we'd map multi layer identifier here
    name = get_relation_identifier_name(logical_plan.name())
    full_table_identifier = get_relation_identifier_name(
        logical_plan.name(), is_multi_part=True
    )
    comment = logical_plan.tableSpec().comment()

    container = execute_logical_plan(logical_plan.query())
    df = container.dataframe
    columns = container.column_map.snowpark_to_spark_map().items()
    for orig_column, user_column in columns:
        df = df.with_column_renamed(
            orig_column, spark_to_sf_single_id(user_column, is_column=True)
        )

    # TODO escaping should be handled by snowpark. remove when SNOW-2210271 is done
    def _escape(comment: str) -> str:
        return comment.replace("\\", "\\\\")

    df.write.save_as_table(
        name,
        comment=None if comment.isEmpty() else _escape(comment.get()),
        mode=mode,
    )

    # Record table metadata for CREATE TABLE AS SELECT
    # These are typically considered v2 tables and support RENAME COLUMN
    record_table_metadata(
        table_identifier=full_table_identifier,
        table_type="v2",
        data_source="default",
        supports_column_rename=True,
    )


def _spark_field_to_sql(field: jpype.JObject, is_column: bool) -> str:
    # Column names will be uppercased according to "snowpark.connect.sql.identifiers.auto-uppercase",
    # and struct fields will be left as is. This should allow users to use the same names
    # in spark and Snowflake in most cases.
    if is_column:
        name = spark_to_sf_single_id(str(field.name()), is_column=True)
    else:
        name = quote_name_without_upper_casing(str(field.name()))
    data_type_str = _spark_datatype_to_sql(field.dataType())
    # TODO: Support comments
    return f"{name} {data_type_str}"


def _spark_datatype_to_sql(data_type: jpype.JObject) -> str:
    match data_type.typeName():
        case "array":
            element_type_str = _spark_datatype_to_sql(data_type.elementType())
            return f"ARRAY({element_type_str})"
        case "map":
            key_type_str = _spark_datatype_to_sql(data_type.keyType())
            value_type_str = _spark_datatype_to_sql(data_type.valueType())
            return f"MAP({key_type_str}, {value_type_str})"
        case "struct":
            field_types_str = ", ".join(
                _spark_field_to_sql(f, False) for f in data_type.fields()
            )
            return f"OBJECT({field_types_str})"
        case _:
            return data_type.sql()


def _normalize_identifiers(node):
    """
    Fix spark-quoted identifiers parsed with sqlglot.

    sqlglot detects quoted spark identifiers which makes them quoted in the Snowflake SQL string.
    This behaviour is not consistent with Spark, where non-column identifiers are case insensitive.
    The identifiers need to be uppercased to match Snowflake's behaviour. Users can disable this by setting
    the `snowpark.connect.auto_uppercase_ddl` config to False.
    """
    if not isinstance(node, Identifier):
        return node
    elif auto_uppercase_non_column_identifiers():
        return Identifier(this=node.this.upper(), quoted=True)
    else:
        return Identifier(this=node.this, quoted=True)


def _remove_file_format_property(node):
    """
    Fix spark-quoted identifiers parsed with sqlglot.

    sqlglot detects quoted spark identifiers which makes them quoted in the Snowflake SQL string.
    This behaviour is not consistent with Spark, where non-column identifiers are case insensitive.
    The identifiers need to be uppercased to match Snowflake's behaviour. Users can disable this by setting
    the `snowpark.connect.auto_uppercase_ddl` config to False.
    """
    if isinstance(node, FileFormatProperty):
        return None
    return node


def _remove_column_data_type(node):
    """
    Fix spark-quoted identifiers parsed with sqlglot.

    sqlglot detects quoted spark identifiers which makes them quoted in the Snowflake SQL string.
    This behaviour is not consistent with Spark, where non-column identifiers are case insensitive.
    The identifiers need to be uppercased to match Snowflake's behaviour. Users can disable this by setting
    the `snowpark.connect.auto_uppercase_ddl` config to False.
    """
    if isinstance(node, DataType) and isinstance(node.parent, ColumnDef):
        return None
    return node


def _get_condition_from_action(action, column_mapping, typer):
    condition = None
    if action.condition().isDefined():
        (_, condition_typed_col,) = map_single_column_expression(
            map_logical_plan_expression(action.condition().get()),
            column_mapping,
            typer,
        )
        condition = condition_typed_col.col
    return condition


def _get_assignments_from_action(
    action,
    column_mapping_source,
    column_mapping_target,
    typer_source,
    typer_target,
):
    assignments = dict()
    if (
        action.getClass().getSimpleName() == "InsertAction"
        or action.getClass().getSimpleName() == "UpdateAction"
    ):
        incoming_assignments = as_java_list(action.assignments())
        for assignment in incoming_assignments:
            (_, key_typ_col) = map_single_column_expression(
                map_logical_plan_expression(assignment.key()),
                column_mapping=column_mapping_target,
                typer=typer_target,
            )
            key_name = typer_target.df.select(key_typ_col.col).columns[0]

            (_, val_typ_col) = map_single_column_expression(
                map_logical_plan_expression(assignment.value()),
                column_mapping=column_mapping_source,
                typer=typer_source,
            )

            assignments[key_name] = val_typ_col.col
    elif (
        action.getClass().getSimpleName() == "InsertStarAction"
        or action.getClass().getSimpleName() == "UpdateStarAction"
    ):
        if len(column_mapping_source.columns) != len(column_mapping_target.columns):
            raise ValueError(
                "source and target must have the same number of columns for InsertStarAction or UpdateStarAction"
            )
        for i, col in enumerate(column_mapping_target.columns):
            if assignments.get(col.snowpark_name) is not None:
                raise SnowparkConnectNotImplementedError(
                    "UpdateStarAction or InsertStarAction is not supported with duplicate columns."
                )
            assignments[col.snowpark_name] = snowpark_fn.col(
                column_mapping_source.columns[i].snowpark_name
            )
    return assignments


def map_sql_to_pandas_df(
    sql_string: str,
    named_args: MutableMapping[str, expressions_proto.Expression.Literal],
    pos_args: MutableSequence[expressions_proto.Expression.Literal],
) -> tuple[pandas.DataFrame, str] | tuple[None, None]:
    """
    Convert a sql string into a pandas DataFrame and its json schema.
    returns a tuple of empty Pandas DataFrame and schema string in case of DDL statements.
    returns a tuple of None for SELECT queries to enable lazy evaluation
    """

    snowpark_connect_sql_passthrough, sql_string = is_valid_passthrough_sql(sql_string)

    if not snowpark_connect_sql_passthrough:
        logical_plan = sql_parser().parsePlan(sql_string)
        parsed_pos_args = parse_pos_args(logical_plan, pos_args)
        set_sql_args(named_args, parsed_pos_args)

        session = get_or_create_snowpark_session()

        rows: list | None = None

        while (
            class_name := str(logical_plan.getClass().getSimpleName())
        ) == "UnresolvedHint":
            logical_plan = logical_plan.child()

        # TODO: Add support for temporary views for SQL cases such as ShowViews, ShowColumns ect. (Currently the cases are not compatible with Spark, returning raw Snowflake rows)
        match class_name:
            case "AddColumns":
                # Handle ALTER TABLE ... ADD COLUMNS (col_name data_type) -> ADD COLUMN col_name data_type
                table_name = get_relation_identifier_name(logical_plan.table(), True)

                # Get column definitions from logical plan
                columns_to_add = logical_plan.columnsToAdd()
                # Build Snowflake SQL from logical plan attributes
                for col in as_java_list(columns_to_add):
                    # Follow the same pattern as AlterColumn for column name extraction
                    col_name = ".".join(
                        spark_to_sf_single_id(part, is_column=True)
                        for part in as_java_list(col.name())
                    )
                    col_type = _spark_datatype_to_sql(col.dataType())
                    snowflake_sql = (
                        f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    )
                    session.sql(snowflake_sql).collect()
            case "AlterColumn":
                # Handle ALTER TABLE ... CHANGE COLUMN (translate to ALTER TABLE ... ALTER COLUMN)
                table_name = get_relation_identifier_name(logical_plan.table(), True)
                column_obj = logical_plan.column()

                # Extract actual column name
                column_name = ".".join(
                    spark_to_sf_single_id(part, is_column=True)
                    for part in as_java_list(column_obj.name())
                )

                if not global_config.spark_sql_caseSensitive:
                    case_insensitive_name = next(
                        (
                            f.name
                            for f in session.table(table_name).schema.fields
                            if f.name.lower() == column_name.lower()
                        ),
                        None,
                    )
                    if case_insensitive_name:
                        column_name = case_insensitive_name

                # Build ALTER COLUMN command from logical plan attributes
                alter_parts = []

                # Check for comment change - Scala Some() vs None
                comment_obj = logical_plan.comment()
                if (
                    comment_obj is not None
                    and str(comment_obj.getClass().getSimpleName()) == "Some"
                ):
                    comment = _escape_sql_comment(str(comment_obj.get()))
                    alter_parts.append(f"COMMENT '{comment}'")

                # Check for dataType change - handle Scala Some/None
                data_type_obj = logical_plan.dataType()
                if (
                    data_type_obj is not None
                    and str(data_type_obj.getClass().getSimpleName()) == "Some"
                ):
                    # Extract the actual data type from Scala Some()
                    actual_data_type = data_type_obj.get()
                    data_type = _spark_datatype_to_sql(actual_data_type)
                    alter_parts.append(f"TYPE {data_type}")

                if alter_parts:
                    alter_clause = ", ".join(alter_parts)
                    snowflake_sql = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} {alter_clause}"
                    session.sql(snowflake_sql).collect()
                else:
                    raise ValueError(
                        f"No alter operations found in AlterColumn logical plan for table {table_name}, column {column_name}"
                    )
            case "CreateNamespace":
                name = get_relation_identifier_name(logical_plan.name(), True)
                previous_name = session.connection.schema
                if_not_exists = "IF NOT EXISTS " if logical_plan.ifNotExists() else ""
                session.sql(f"CREATE SCHEMA {if_not_exists}{name}").collect()
                if previous_name is not None:
                    session.sql(f"USE SCHEMA {quote_name(previous_name)}").collect()
                else:
                    # TODO: Unset the schema
                    pass
            case "CreateTable" | "ReplaceTable":
                if class_name == "ReplaceTable":
                    replace_table = " OR REPLACE "
                    if_not_exists = ""
                else:
                    replace_table = ""
                    if_not_exists = (
                        "IF NOT EXISTS " if logical_plan.ignoreIfExists() else ""
                    )

                name = get_relation_identifier_name(logical_plan.name())
                full_table_identifier = get_relation_identifier_name(
                    logical_plan.name(), is_multi_part=True
                )
                columns = ", ".join(
                    _spark_field_to_sql(f, True)
                    for f in logical_plan.tableSchema().fields()
                )
                comment_opt = logical_plan.tableSpec().comment()
                comment = (
                    f"COMMENT = '{_escape_sql_comment(str(comment_opt.get()))}'"
                    if comment_opt.isDefined()
                    else ""
                )

                # Extract data source for metadata tracking
                data_source = "default"

                with suppress(Exception):
                    # Get data source from tableSpec.provider() (for USING clause)
                    if hasattr(logical_plan, "tableSpec"):
                        table_spec = logical_plan.tableSpec()
                        if hasattr(table_spec, "provider"):
                            provider_opt = table_spec.provider()
                            if provider_opt.isDefined():
                                data_source = str(provider_opt.get()).lower()
                        else:
                            # Fall back to checking properties for FORMAT
                            table_properties = table_spec.properties()
                            if not table_properties.isEmpty():
                                for prop in table_properties.get():
                                    if str(prop.key()) == "FORMAT":
                                        data_source = str(prop.value()).lower()
                                        break

                # NOTE: We are intentionally ignoring any FORMAT=... parameters here.
                session.sql(
                    f"CREATE {replace_table} TABLE {if_not_exists}{name} ({columns}) {comment}"
                ).collect()

                # Record table metadata for Spark compatibility
                # Tables created with explicit schema are considered v1 tables
                # v1 tables with certain data sources don't support RENAME COLUMN in OSS Spark
                supports_rename = data_source not in (
                    "parquet",
                    "csv",
                    "json",
                    "orc",
                    "avro",
                )
                record_table_metadata(
                    table_identifier=full_table_identifier,
                    table_type="v1",
                    data_source=data_source,
                    supports_column_rename=supports_rename,
                )
            case "CreateTableAsSelect":
                mode = "ignore" if logical_plan.ignoreIfExists() else "errorifexists"
                _create_table_as_select(logical_plan, mode=mode)
            case "CreateTableLikeCommand":
                source = get_relation_identifier_name(logical_plan.sourceTable())
                name = get_relation_identifier_name(logical_plan.targetTable())
                if_not_exists = "IF NOT EXISTS " if logical_plan.ifNotExists() else ""
                session.sql(
                    f"CREATE TABLE {if_not_exists}{name} LIKE {source}"
                ).collect()
            case "CreateTempViewUsing":
                empty_select = (
                    " AS SELECT * WHERE 1 = 0"
                    if logical_plan.options().isEmpty()
                    and logical_plan.children().isEmpty()
                    else ""
                )
                parsed_sql = (
                    sqlglot.parse_one(sql_string, dialect="spark")
                    .transform(_normalize_identifiers)
                    .transform(_remove_column_data_type)
                    .transform(_remove_file_format_property)
                )
                snowflake_sql = parsed_sql.sql(dialect="snowflake")
                session.sql(f"{snowflake_sql}{empty_select}").collect()
                spark_view_name = next(
                    sqlglot.parse_one(sql_string, dialect="spark").find_all(
                        sqlglot.exp.Table
                    )
                ).name
                snowflake_view_name = spark_to_sf_single_id_with_unquoting(
                    spark_view_name
                )
                temp_view = get_temp_view(snowflake_view_name)
                if temp_view is not None and not logical_plan.replace():
                    raise AnalysisException(
                        f"[TEMP_TABLE_OR_VIEW_ALREADY_EXISTS] Cannot create the temporary view `{spark_view_name}` because it already exists."
                    )
                else:
                    unregister_temp_view(
                        spark_to_sf_single_id_with_unquoting(spark_view_name)
                    )
            case "CreateView":
                current_schema = session.connection.schema
                if (
                    str(logical_plan.child().getClass().getSimpleName())
                    == "PlanWithUnresolvedIdentifier"
                ):
                    object_name: str = str(
                        logical_plan.child().identifierExpr().value()
                    )
                else:
                    object_name: str = as_java_list(logical_plan.child().nameParts())[0]
                _accessing_temp_object.set(False)
                df_container = execute_logical_plan(logical_plan.query())
                df = df_container.dataframe
                if _accessing_temp_object.get():
                    raise AnalysisException(
                        f"[INVALID_TEMP_OBJ_REFERENCE] Cannot create the persistent object `{CURRENT_CATALOG_NAME}`.`{current_schema}`.`{object_name}` "
                        "of the type VIEW because it references to a temporary object of the type VIEW. Please "
                        f"make the temporary object persistent, or make the persistent object `{CURRENT_CATALOG_NAME}`.`{current_schema}`.`{object_name}` temporary."
                    )

                name = get_relation_identifier_name(logical_plan.child())
                comment = logical_plan.comment()

                df = _rename_columns(
                    df, logical_plan.userSpecifiedColumns(), df_container.column_map
                )

                # TODO: Support logical_plan.replace() == False
                df.create_or_replace_view(
                    name,
                    comment=_escape_sql_comment(str(comment.get()))
                    if comment.isDefined()
                    else None,
                )
            case "CreateViewCommand":
                with push_processed_view(logical_plan.name().identifier()):
                    df_container = execute_logical_plan(logical_plan.plan())
                    df = df_container.dataframe
                    user_specified_spark_column_names = [
                        str(col._1())
                        for col in as_java_list(logical_plan.userSpecifiedColumns())
                    ]
                    df_container = DataFrameContainer.create_with_column_mapping(
                        dataframe=df,
                        spark_column_names=user_specified_spark_column_names
                        if user_specified_spark_column_names
                        else df_container.column_map.get_spark_columns(),
                        snowpark_column_names=df_container.column_map.get_snowpark_columns(),
                        parent_column_name_map=df_container.column_map,
                    )
                    is_global = isinstance(
                        logical_plan.viewType(),
                        jpype.JClass(
                            "org.apache.spark.sql.catalyst.analysis.GlobalTempView$"
                        ),
                    )
                    if is_global:
                        view_name = [
                            global_config.spark_sql_globalTempDatabase,
                            logical_plan.name().quotedString(),
                        ]
                    else:
                        view_name = [logical_plan.name().quotedString()]
                    view_name = [
                        spark_to_sf_single_id_with_unquoting(part) for part in view_name
                    ]
                    joined_view_name = ".".join(view_name)

                    register_temp_view(
                        joined_view_name,
                        df_container,
                        logical_plan.replace(),
                    )
                    tmp_views = _get_current_temp_objects()
                    tmp_views.add(
                        (
                            CURRENT_CATALOG_NAME,
                            session.connection.schema,
                            str(logical_plan.name().identifier()),
                        )
                    )
            case "DescribeColumn":
                name = get_relation_identifier_name_without_uppercasing(
                    logical_plan.column()
                )
                if get_temp_view(name):
                    return SNOWFLAKE_CATALOG.listColumns(unquote_if_quoted(name)), ""
                # todo double check if this is correct
                name = get_relation_identifier_name(logical_plan.column())
                rows = session.sql(f"DESCRIBE TABLE {name}").collect()
            case "DescribeNamespace":
                name = get_relation_identifier_name(logical_plan.namespace(), True)
                rows = session.sql(f"DESCRIBE SCHEMA {name}").collect()
                if not rows:
                    rows = None
            case "DescribeRelation":
                name = get_relation_identifier_name(logical_plan.relation(), True)
                rows = session.sql(f"DESCRIBE TABLE {name}").collect()
                if not rows:
                    rows = None
            case "DescribeQueryCommand":
                # Handle DESCRIBE QUERY <sql> commands
                # Since Snowflake doesn't support DESCRIBE QUERY syntax, we use DataFrame schema analysis
                # This gets the schema without executing the query (similar to Spark's DESCRIBE QUERY)
                # Get the inner query plan and convert it to SQL
                inner_query_plan = logical_plan.plan()
                df_container = execute_logical_plan(inner_query_plan)
                df = df_container.dataframe
                schema = df.schema

                # Get original Spark column names using the column map from the original DataFrame
                spark_columns = df_container.column_map.get_spark_columns()
                data = []
                for i, field in enumerate(schema.fields):
                    # Use original Spark column name from column map
                    col_name = spark_columns[i]

                    # Convert Snowpark data type to PySpark data type and get simpleString
                    pyspark_type = map_snowpark_to_pyspark_types(field.datatype)
                    data_type_str = pyspark_type.simpleString()

                    data.append(
                        {
                            "col_name": col_name,
                            "data_type": data_type_str,
                            "comment": None,  # Snowflake schema doesn't include comments
                        }
                    )
                return pandas.DataFrame(data), ""
            case "DropFunctionCommand":
                func_name = logical_plan.identifier().funcName().lower()
                input_types, snowpark_name = [], ""
                if func_name in session._udfs:
                    input_types, snowpark_name = (
                        session._udfs[func_name].input_types,
                        session._udfs[func_name].name,
                    )
                    del session._udfs[func_name]
                elif func_name in session._udtfs:
                    input_types, snowpark_name = (
                        session._udtfs[func_name][0].input_types,
                        session._udtfs[func_name][0].name,
                    )
                    del session._udtfs[func_name]
                else:
                    if not logical_plan.ifExists():
                        raise ValueError(
                            f"Function {func_name} not found among registered UDFs or UDTFs."
                        )
                if snowpark_name != "":
                    argument_string = f"({', '.join(convert_sp_to_sf_type(arg) for arg in input_types)})"
                    session.sql(
                        f"DROP FUNCTION {'IF EXISTS' if logical_plan.ifExists() else ''} {snowpark_name}{argument_string}"
                    ).collect()
            case "DropNamespace":
                name = get_relation_identifier_name(logical_plan.namespace(), True)
                if_exists = "IF EXISTS " if logical_plan.ifExists() else ""
                session.sql(f"DROP SCHEMA {if_exists}{name}").collect()
            case "DropTable":
                name = get_relation_identifier_name(logical_plan.child())
                if_exists = "IF EXISTS " if logical_plan.ifExists() else ""
                session.sql(f"DROP TABLE {if_exists}{name}").collect()
            case "DropView":
                temporary_view_name = get_relation_identifier_name_without_uppercasing(
                    logical_plan.child()
                )
                if not unregister_temp_view(temporary_view_name):
                    name = get_relation_identifier_name(logical_plan.child())
                    if_exists = "IF EXISTS " if logical_plan.ifExists() else ""
                    session.sql(f"DROP VIEW {if_exists}{name}").collect()
            case "ExplainCommand":
                inner_plan = logical_plan.logicalPlan()
                logical_plan_name = inner_plan.nodeName()

                # Handle EXPLAIN DESCRIBE QUERY commands
                if logical_plan_name == "DescribeQueryCommand":
                    # For EXPLAIN DESCRIBE QUERY, we should return an explanation of the describe operation itself
                    # NOT execute the inner query to get its SQL
                    query_plan = inner_plan.plan()
                    plan_description = (
                        f"Describe query plan for: {query_plan.nodeName()}"
                    )
                    rows = [snowpark.Row(plan=plan_description)]
                elif logical_plan_name == "DescribeRelation":
                    # For EXPLAIN DESCRIBE RELATION, we should return an explanation of the describe operation itself
                    # NOT execute the inner query to get its SQL
                    relation = inner_plan.relation()
                    plan_description = (
                        f"Describe relation plan for: {relation.commandName()}"
                    )
                    rows = [snowpark.Row(plan=plan_description)]
                elif logical_plan_name == "DescribeColumn":
                    # For EXPLAIN DESCRIBE COLUMN, we should return an explanation of the describe operation itself
                    # NOT execute the inner query to get its SQL
                    column = inner_plan.column()
                    plan_description = f"Describe column plan for: [{column.name()}]"
                    rows = [snowpark.Row(plan=plan_description)]
                elif logical_plan_name in (
                    "Project",
                    "Aggregate",
                    "Sort",
                    "UnresolvedWith",
                    "UnresolvedHaving",
                    "Distinct",
                ):
                    expr = execute_logical_plan(
                        logical_plan.logicalPlan()
                    ).dataframe.queries["queries"][0]
                    final_sql = f"EXPLAIN USING TEXT {expr}"
                    rows = session.sql(final_sql).collect()
                elif (
                    logical_plan_name == "InsertIntoStatement"
                    or logical_plan_name == "CreateView"
                ):
                    expr = execute_logical_plan(
                        logical_plan.logicalPlan().query()
                    ).dataframe.queries["queries"][0]
                    final_sql = f"EXPLAIN USING TEXT {expr}"
                    rows = session.sql(final_sql).collect()
                else:
                    # TODO: Support other logical plans
                    raise SnowparkConnectNotImplementedError(
                        f"{logical_plan_name} is not supported yet with EXPLAIN."
                    )
            case "InsertIntoStatement":
                df_container = execute_logical_plan(logical_plan.query())
                df = df_container.dataframe
                queries = df.queries["queries"]
                if len(queries) != 1:
                    raise SnowparkConnectNotImplementedError(
                        f"Unexpected number of queries: {len(queries)}"
                    )

                name = get_relation_identifier_name(logical_plan.table(), True)

                user_columns = [
                    spark_to_sf_single_id(str(col), is_column=True)
                    for col in as_java_list(logical_plan.userSpecifiedCols())
                ]
                overwrite_str = "OVERWRITE" if logical_plan.overwrite() else ""
                cols_str = "(" + ", ".join(user_columns) + ")" if user_columns else ""

                try:
                    target_table = session.table(name)
                    target_schema = target_table.schema

                    # Modify df with NaN → NULL conversion for DECIMAL columns
                    modified_columns = []
                    for source_field, target_field in zip(
                        df.schema.fields, target_schema.fields
                    ):
                        col_name = source_field.name
                        if isinstance(
                            target_field.datatype, snowpark.types.DecimalType
                        ) and isinstance(
                            source_field.datatype,
                            (snowpark.types.FloatType, snowpark.types.DoubleType),
                        ):
                            # Add CASE WHEN to convert NaN to NULL for DECIMAL targets
                            # Only apply this to floating-point source columns
                            modified_col = (
                                snowpark_fn.when(
                                    snowpark_fn.equal_nan(snowpark_fn.col(col_name)),
                                    snowpark_fn.lit(None),
                                )
                                .otherwise(snowpark_fn.col(col_name))
                                .alias(col_name)
                            )
                            modified_columns.append(modified_col)
                        else:
                            modified_columns.append(snowpark_fn.col(col_name))

                    df = df.select(modified_columns)
                except Exception:
                    pass
                queries = df.queries["queries"]
                final_query = queries[0]
                session.sql(
                    f"INSERT {overwrite_str} INTO {name} {cols_str} {final_query}",
                ).collect()
            case "MergeIntoTable":
                source_df_container = map_relation(
                    map_logical_plan_relation(logical_plan.sourceTable())
                )
                source_df = source_df_container.dataframe
                plan_id = gen_sql_plan_id()
                target_df_container = map_relation(
                    map_logical_plan_relation(logical_plan.targetTable(), plan_id)
                )
                target_df = target_df_container.dataframe

                if (
                    logical_plan.targetTable().getClass().getSimpleName()
                    == "UnresolvedRelation"
                ):
                    target_table_name = _spark_to_snowflake(
                        logical_plan.targetTable().multipartIdentifier()
                    )
                else:
                    target_table_name = _spark_to_snowflake(
                        logical_plan.targetTable().child().multipartIdentifier()
                    )

                target_table = session.table(target_table_name)
                target_table_columns = target_table.columns
                target_df_spark_names = []
                for target_table_col, target_df_col in zip(
                    target_table_columns, target_df_container.column_map.columns
                ):
                    target_df = target_df.with_column_renamed(
                        target_df_col.snowpark_name,
                        target_table_col,
                    )
                    target_df_spark_names.append(target_df_col.spark_name)
                target_df_container = DataFrameContainer.create_with_column_mapping(
                    dataframe=target_df,
                    spark_column_names=target_df_spark_names,
                    snowpark_column_names=target_table_columns,
                )

                set_plan_id_map(plan_id, target_df_container)

                joined_df_before_condition: snowpark.DataFrame = source_df.join(
                    target_df
                )

                column_mapping_for_conditions = column_name_handler.JoinColumnNameMap(
                    source_df_container.column_map,
                    target_df_container.column_map,
                )
                typer_for_expressions = ExpressionTyper(joined_df_before_condition)

                (_, merge_condition_typed_col,) = map_single_column_expression(
                    map_logical_plan_expression(logical_plan.mergeCondition()),
                    column_mapping=column_mapping_for_conditions,
                    typer=typer_for_expressions,
                )

                clauses = []

                for matched_action in as_java_list(logical_plan.matchedActions()):
                    condition = _get_condition_from_action(
                        matched_action,
                        column_mapping_for_conditions,
                        typer_for_expressions,
                    )
                    if matched_action.getClass().getSimpleName() == "DeleteAction":
                        clauses.append(when_matched(condition).delete())
                    elif (
                        matched_action.getClass().getSimpleName() == "UpdateAction"
                        or matched_action.getClass().getSimpleName()
                        == "UpdateStarAction"
                    ):
                        assignments = _get_assignments_from_action(
                            matched_action,
                            source_df_container.column_map,
                            target_df_container.column_map,
                            ExpressionTyper(source_df),
                            ExpressionTyper(target_df),
                        )
                        clauses.append(when_matched(condition).update(assignments))

                for not_matched_action in as_java_list(
                    logical_plan.notMatchedActions()
                ):
                    condition = _get_condition_from_action(
                        not_matched_action,
                        column_mapping_for_conditions,
                        typer_for_expressions,
                    )
                    if (
                        not_matched_action.getClass().getSimpleName() == "InsertAction"
                        or not_matched_action.getClass().getSimpleName()
                        == "InsertStarAction"
                    ):
                        assignments = _get_assignments_from_action(
                            not_matched_action,
                            source_df_container.column_map,
                            target_df_container.column_map,
                            ExpressionTyper(source_df),
                            ExpressionTyper(target_df),
                        )
                        clauses.append(when_not_matched(condition).insert(assignments))

                if not as_java_list(logical_plan.notMatchedBySourceActions()).isEmpty():
                    raise SnowparkConnectNotImplementedError(
                        "Snowflake does not support 'not matched by source' actions in MERGE statements."
                    )

                target_table.merge(source_df, merge_condition_typed_col.col, clauses)
            case "DeleteFromTable":
                df_container = map_relation(
                    map_logical_plan_relation(logical_plan.table())
                )
                name = get_relation_identifier_name(logical_plan.table(), True)
                table = session.table(name)
                table_columns = table.columns
                df = df_container.dataframe
                spark_names = []
                for table_col, df_col in zip(
                    table_columns, df_container.column_map.columns
                ):
                    df = df.with_column_renamed(
                        df_col.snowpark_name,
                        table_col,
                    )
                    spark_names.append(df_col.spark_name)
                df_container = DataFrameContainer.create_with_column_mapping(
                    dataframe=df,
                    spark_column_names=spark_names,
                    snowpark_column_names=table_columns,
                )
                df = df_container.dataframe
                (
                    condition_column_name,
                    condition_typed_col,
                ) = map_single_column_expression(
                    map_logical_plan_expression(logical_plan.condition()),
                    df_container.column_map,
                    ExpressionTyper(df),
                )
                table.delete(condition_typed_col.col)
            case "UpdateTable":
                # Databricks/Delta-specific extension not supported by SAS.
                # Provide an actionable, clear error.
                raise UnsupportedOperationException(
                    "[UNSUPPORTED_SQL_EXTENSION] The UPDATE TABLE command failed.\n"
                    + "Reason: This command is a platform-specific SQL extension and is not part of the standard Apache Spark specification that this interface uses."
                )
            case "RenameColumn":
                full_table_identifier = get_relation_identifier_name(
                    logical_plan.table(), True
                )

                # Check Spark compatibility for RENAME COLUMN operation
                if not check_table_supports_operation(
                    full_table_identifier, "rename_column"
                ):
                    raise AnalysisException(
                        f"ALTER TABLE RENAME COLUMN is not supported for table '{full_table_identifier}'. "
                        f"This table was created as a v1 table with a data source that doesn't support column renaming. "
                        f"To enable this operation, set 'snowpark.connect.enable_snowflake_extension_behavior' to 'true'."
                    )

                column_obj = logical_plan.column()
                old_column_name = ".".join(
                    spark_to_sf_single_id(str(part), is_column=True)
                    for part in as_java_list(column_obj.name())
                )
                if not global_config.spark_sql_caseSensitive:
                    case_insensitive_name = next(
                        (
                            f.name
                            for f in session.table(full_table_identifier).schema.fields
                            if f.name.lower() == old_column_name.lower()
                        ),
                        None,
                    )
                    if case_insensitive_name:
                        old_column_name = case_insensitive_name
                new_column_name = spark_to_sf_single_id(
                    str(logical_plan.newName()), is_column=True
                )

                # Pass through to Snowflake
                snowflake_sql = f"ALTER TABLE {full_table_identifier} RENAME COLUMN {old_column_name} TO {new_column_name}"
                session.sql(snowflake_sql).collect()
            case "RenameTable":
                name = get_relation_identifier_name(logical_plan.child(), True)
                new_name = _spark_to_snowflake(logical_plan.newName())

                try:
                    session.sql(f"ALTER TABLE {name} RENAME TO {new_name}").collect()
                except Exception as e:
                    # This is a trick to rename iceberg tables without having to first sacrifice a query to determine
                    # whether the source table is an iceberg table.
                    # TODO(SNOW-2118744): such keyword is required for other ALTER TABLE commands against Iceberg tables
                    # too.
                    if str(e).find("is an Iceberg table") >= 0:
                        session.sql(
                            f"ALTER ICEBERG TABLE {name} RENAME TO {new_name}"
                        ).collect()
                    else:
                        raise e
            case "ReplaceTableAsSelect":
                _create_table_as_select(logical_plan, mode="overwrite")
            case "ResetCommand":
                key = logical_plan.config().get()
                unset_config_param(get_session_id(), key, session)
            case "SetCatalogAndNamespace":
                # TODO: add catalog setting here
                name = get_relation_identifier_name(logical_plan.child(), True)
                session.sql(f"USE SCHEMA {name}").collect()
            case "SetCommand":
                kv_result_tuple = logical_plan.kv().get()
                key = kv_result_tuple._1()
                val = kv_result_tuple._2().get()
                set_config_param(get_session_id(), key, val, session)
            case "SetNamespaceCommand":
                name = _spark_to_snowflake(logical_plan.namespace())
                session.sql(f"USE SCHEMA {name}").collect()
            case "SetNamespaceLocation" | "SetNamespaceProperties":
                raise SnowparkConnectNotImplementedError(
                    "Altering databases is not currently supported."
                )
            case "ShowCreateTable":
                # Handle SHOW CREATE TABLE command
                # Spark: SHOW CREATE TABLE table_name
                # Snowflake: SELECT get_ddl('table', 'table_name')
                table_relation = logical_plan.child()
                table_name = _spark_to_snowflake(table_relation.multipartIdentifier())

                # Convert to Snowflake get_ddl function
                snowflake_sql = f"SELECT get_ddl('table', '{table_name}') AS ddl"
                rows = session.sql(snowflake_sql).collect()

            case "ShowCurrentNamespaceCommand":
                name = session.get_current_schema()
                unquoted_name = unquote_if_quoted(name)
                sql = f"SHOW SCHEMAS LIKE '{unquoted_name}'"
                rows = session.sql(sql).collect()
                if not rows:
                    rows = None
            case "ShowNamespaces":
                name = get_relation_identifier_name(logical_plan.namespace(), True)
                if name:
                    raise SnowparkConnectNotImplementedError(
                        "'IN' clause is not supported while listing databases"
                    )
                if logical_plan.pattern().isDefined():
                    # Snowflake SQL requires a "%" pattern.
                    # Snowpark catalog requires a regex and does client-side filtering.
                    # Spark, however, uses a regex-like pattern that treats '*' and '|' differently.
                    raise SnowparkConnectNotImplementedError(
                        "'LIKE' clause is not supported while listing databases"
                    )
                rows = session.sql("SHOW SCHEMAS").collect()
                if not rows:
                    rows = None
            case "ShowTables" | "ShowTableExtended":
                name = get_relation_identifier_name(logical_plan.namespace(), True)

                # Get the pattern for filtering
                pattern = None
                if class_name == "ShowTables" and logical_plan.pattern().isDefined():
                    pattern = logical_plan.pattern().get()
                elif (
                    class_name == "ShowTableExtended"
                    and len(logical_plan.pattern()) != 0
                ):
                    pattern = logical_plan.pattern()

                # Execute SHOW TABLES command
                if name:
                    rows = session.sql(f"SHOW TABLES IN {name}").collect()
                else:
                    rows = session.sql("SHOW TABLES").collect()

                # Return empty DataFrame with proper schema if no results
                if not rows:
                    if class_name == "ShowTableExtended":
                        return (
                            pandas.DataFrame(
                                {
                                    "namespace": [""],
                                    "tableName": [""],
                                    "isTemporary": [""],
                                    "information": [""],
                                }
                            ),
                            "",
                        )
                    else:
                        return (
                            pandas.DataFrame(
                                {
                                    "namespace": [""],
                                    "tableName": [""],
                                    "isTemporary": [""],
                                }
                            ),
                            "",
                        )

                # Apply pattern filtering if pattern is provided
                # This is workaround to filter using Python regex.
                if pattern and rows:
                    rows = _filter_tables_by_pattern(rows, pattern)
            case "ShowViews":
                name = get_relation_identifier_name(logical_plan.namespace(), True)

                # Get the pattern for filtering
                pattern = (
                    logical_plan.pattern().get()
                    if logical_plan.pattern().isDefined()
                    else None
                )

                # Execute SHOW VIEWS command
                if name:
                    rows = session.sql(f"SHOW VIEWS IN {name}").collect()
                else:
                    rows = session.sql("SHOW VIEWS").collect()

                # Apply pattern filtering if pattern is provided
                if pattern and rows:
                    rows = _filter_tables_by_pattern(rows, pattern)
            case "ShowColumns":
                # Handle Spark SQL: SHOW COLUMNS IN table_name FROM database_name
                # Convert to Snowflake SQL: SHOW COLUMNS IN TABLE database_name.table_name

                # Extract table name from ShowColumns logical plan
                # The child() is an UnresolvedTable object, use the existing helper function
                table_relation = logical_plan.child()
                db_and_table_name = as_java_list(table_relation.multipartIdentifier())
                multi_part_len = len(db_and_table_name)
                table_name = _spark_to_snowflake(table_relation.multipartIdentifier())

                db_name = None
                # Get database name if specified in namespace
                if logical_plan.namespace().isDefined():
                    db_namespace = logical_plan.namespace().get()
                    db_name = _spark_to_snowflake(db_namespace)

                # Build the Snowflake SHOW COLUMNS command
                if db_name and multi_part_len == 1:
                    # Full qualified table name: db.table
                    full_table_name = f"{db_name}.{table_name}"
                    snowflake_cmd = f"SHOW COLUMNS IN TABLE {full_table_name}"
                else:
                    if db_name and multi_part_len == 2:
                        # Check db_name is same as in the full table name
                        if (
                            spark_to_sf_single_id(str(db_and_table_name[0])).casefold()
                            != db_name.casefold()
                        ):
                            raise AnalysisException(
                                f"database name is not matching:{db_name} and {db_and_table_name[0]}"
                            )

                            # Just table name
                    snowflake_cmd = f"SHOW COLUMNS IN TABLE {table_name}"

                rows = session.sql(snowflake_cmd).collect()
            case "TruncateTable":
                name = get_relation_identifier_name(logical_plan.table(), True)
                session.sql(f"TRUNCATE TABLE {name}").collect()

            case command if (
                command.startswith("Alter")
                or command.startswith("Create")
                or command.startswith("Drop")
                or command.startswith("Rename")
                or command.startswith("Replace")
                or command.startswith("Set")
                or command.startswith("Truncate")
                or command.startswith("AddColumns")
            ):
                parsed_sql = sqlglot.parse_one(sql_string, dialect="spark").transform(
                    _normalize_identifiers
                )
                snowflake_sql = parsed_sql.sql(dialect="snowflake")
                session.sql(snowflake_sql).collect()
            case command if command.startswith("Describe") or command.startswith(
                "Show"
            ):
                parsed_sql = sqlglot.parse_one(sql_string, dialect="spark").transform(
                    _normalize_identifiers
                )
                snowflake_sql = parsed_sql.sql(dialect="snowflake")
                if command.startswith("Show"):
                    if snowflake_sql.startswith("SHOW TBLPROPERTIES"):
                        # Snowflake doesn't support TBLPROPERTIES, EXTENDED.
                        return pandas.DataFrame({"": [""]}), ""

                rows = session.sql(snowflake_sql).collect()
            case "RefreshTable":
                table_name_unquoted = ".".join(
                    str(part)
                    for part in as_java_list(logical_plan.child().multipartIdentifier())
                )
                SNOWFLAKE_CATALOG.refreshTable(table_name_unquoted)

                return pandas.DataFrame({"": [""]}), ""
            case _:
                execute_logical_plan(logical_plan)
                return None, None
    else:
        # spark.sql("select or cte+select") queries should be executed lazily.
        # This returns an empty dataframe and empty schema.
        # if is_sql_select_statement(_trim_sql_string(sql_string)):
        if _is_sql_select_statement_helper(sql_string):
            return None, None
        session = snowpark.Session.get_active_session()
        rows = session.sql(sql_string).collect()
    if rows:
        return pandas.DataFrame(rows), ""
    return pandas.DataFrame({"": [""]}), ""


def get_sql_passthrough() -> bool:
    return get_boolean_session_config_param("snowpark.connect.sql.passthrough")


def is_valid_passthrough_sql(sql_stmt: str) -> Tuple[bool, str]:
    """
    Checks if :param sql_stmt: should be executed as SQL pass-through. SQL pass-through can be detected in 1 of 2 ways:
    1) Either Spark config parameter "snowpark.connect.sql.passthrough" is set (legacy mode, to be deprecated)
    2) If :param sql_stmt: is created through SnowflakeSession and has correct marker + checksum
    """
    if get_sql_passthrough():
        # legacy style pass-through, sql_stmt should be a whole, valid SQL statement
        return True, sql_stmt

    # check for new style, SnowflakeSession based SQL pass-through
    sql_parts = sql_stmt.split(" ", 2)
    if len(sql_parts) == 3:
        marker, checksum, sql = sql_parts
        if marker == SQL_PASS_THROUGH_MARKER and checksum == calculate_checksum(sql):
            return True, sql

    # Not a SQL pass-through
    return False, sql_stmt


def change_default_to_public(name: str) -> str:
    """
    Change the namespace to PUBLIC when given name is DEFAULT
    :param name: Given namespace
    :return: if name is DEFAULT return PUBLIC otherwise name
    """
    if name.startswith('"'):
        if name.upper() == '"DEFAULT"':
            return name.replace("DEFAULT", "PUBLIC")
    elif name.upper() == "DEFAULT":
        return "PUBLIC"
    return name


def _preprocess_identifier_calls(sql_query: str) -> str:
    """
    Pre-process SQL query to resolve IDENTIFIER() calls before Spark parsing.

    Transforms: IDENTIFIER('abs')(c2) -> abs(c2)
    Transforms: IDENTIFIER('COAL' || 'ESCE')(NULL, 1) -> COALESCE(NULL, 1)

    This preserves all function arguments in their original positions, eliminating
    the need to reconstruct them at the expression level.
    """
    import re

    # Pattern to match IDENTIFIER(...) followed by optional function call arguments
    # This captures both the identifier expression and any trailing arguments
    # Note: We need to be careful about whitespace preservation
    identifier_pattern = r"IDENTIFIER\s*\(\s*([^)]+)\s*\)(\s*)(\([^)]*\))?"

    def resolve_identifier_match(match):
        identifier_expr_str = match.group(1).strip()
        whitespace = match.group(2) if match.group(2) else ""
        function_args = match.group(3) if match.group(3) else ""

        try:
            # Handle string concatenation FIRST: IDENTIFIER('COAL' || 'ESCE')
            # (Must check this before simple strings since it also starts/ends with quotes)
            if "||" in identifier_expr_str:
                # Parse basic string concatenation with proper quote handling
                parts = []
                split_parts = identifier_expr_str.split("||")
                for part in split_parts:
                    part = part.strip()
                    if part.startswith("'") and part.endswith("'"):
                        unquoted = part[1:-1]  # Remove quotes from each part
                        parts.append(unquoted)
                    else:
                        # Non-string parts - return original for safety
                        return match.group(0)
                resolved_name = "".join(parts)  # Concatenate the unquoted parts

            # Handle simple string literals: IDENTIFIER('abs')
            elif identifier_expr_str.startswith("'") and identifier_expr_str.endswith(
                "'"
            ):
                resolved_name = identifier_expr_str[1:-1]  # Remove quotes

            else:
                # Complex expressions not supported yet - return original
                return match.group(0)

            # Return resolved function call with preserved arguments and whitespace
            if function_args:
                # Function call case: IDENTIFIER('abs')(c1) -> abs(c1)
                result = f"{resolved_name}{function_args}"
            else:
                # Column reference case: IDENTIFIER('c1') FROM -> c1 FROM (preserve whitespace)
                result = f"{resolved_name}{whitespace}"
            return result

        except Exception:
            # Return original to avoid breaking the query
            return match.group(0)

    # Apply the transformation
    processed_query = re.sub(
        identifier_pattern, resolve_identifier_match, sql_query, flags=re.IGNORECASE
    )

    return processed_query


def map_sql(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Map a SQL string to a DataFrame.

    The SQL string is executed and the resulting DataFrame is returned.

    In passthough mode as True, SAS calls session.sql() and not calling Spark Parser.
    This is to mitigate any issue not covered by spark logical plan to protobuf conversion.
    """
    snowpark_connect_sql_passthrough, sql_stmt = is_valid_passthrough_sql(rel.sql.query)

    if not snowpark_connect_sql_passthrough:
        logical_plan = sql_parser().parseQuery(sql_stmt)

        parsed_pos_args = parse_pos_args(logical_plan, rel.sql.pos_args)
        set_sql_args(rel.sql.args, parsed_pos_args)

        return execute_logical_plan(logical_plan)
    else:
        session = snowpark.Session.get_active_session()
        sql_df = session.sql(sql_stmt)
        columns = sql_df.columns
        return DataFrameContainer.create_with_column_mapping(
            dataframe=sql_df,
            spark_column_names=columns,
            snowpark_column_names=columns,
        )


def map_logical_plan_relation(
    rel, plan_id: int | None = None
) -> relation_proto.Relation:
    if plan_id is None:
        plan_id = gen_sql_plan_id()
    session = get_or_create_snowpark_session()

    class_name = str(rel.getClass().getSimpleName())
    match class_name:
        case "Aggregate":
            with push_sql_scope():
                input = map_logical_plan_relation(rel.child())

                # For LCA support in GROUP BY, we need to extract aliases from the aggregate expressions
                # In Spark SQL, when you write "SELECT a as k, COUNT(b) FROM table GROUP BY k",
                # the aliases are defined in the aggregateExpressions, not in a separate Project node
                alias_map = {}

                # Extract aliases from the aggregate expressions (SELECT clause)
                alias_map = {}
                for agg_expr in as_java_list(rel.aggregateExpressions()):
                    if str(agg_expr.getClass().getSimpleName()) == "Alias":
                        alias_map[str(agg_expr.name())] = agg_expr.child()

                def substitute_lca_in_grouping_expr(expr):
                    """Substitute LCA references with original expressions and handle ordinal references"""
                    expr_class = str(expr.getClass().getSimpleName())

                    # Handle ordinal references (e.g., GROUP BY 1, GROUP BY 2)
                    # Note: Quoted column names like GROUP BY "1" come through as UnresolvedAttribute,
                    # while unquoted ordinals like GROUP BY 1 come through as Literal with integer type
                    if expr_class == "Literal":
                        # Check if this is an integer literal (ordinal reference)
                        if hasattr(expr, "dataType") and str(
                            expr.dataType().typeName()
                        ) in ["integer", "long"]:
                            ordinal_pos = expr.value()
                            agg_expressions = as_java_list(rel.aggregateExpressions())

                            # Validate ordinal is in valid range (1-based indexing)
                            if isinstance(ordinal_pos, int) and 1 <= ordinal_pos <= len(
                                agg_expressions
                            ):
                                # Return the expression from the SELECT clause at the ordinal position
                                target_expr = agg_expressions[
                                    ordinal_pos - 1
                                ]  # Convert to 0-based index

                                # If the target expression is an alias, return the underlying expression
                                if (
                                    str(target_expr.getClass().getSimpleName())
                                    == "Alias"
                                ):
                                    return target_expr.child()
                                else:
                                    return target_expr
                            # If ordinal is out of range, let it fall through to generate an error later

                    # Handle named LCA references (existing logic)
                    # This handles cases like GROUP BY "1" (quoted column names)
                    if expr_class != "UnresolvedAttribute":
                        return expr

                    attr_parts = as_java_list(expr.nameParts())
                    if len(attr_parts) == 1:
                        attr_name = str(attr_parts[0])
                        return alias_map.get(attr_name, expr)

                    return expr

                group_type = snowflake_proto.Aggregate.GROUP_TYPE_GROUPBY

                grouping_sets: list[snowflake_proto.Aggregate.GroupingSets] = []

                group_expression_list = as_java_list(rel.groupingExpressions())
                for exp in group_expression_list:
                    match str(exp.getClass().getSimpleName()):
                        case "Rollup":
                            group_type = snowflake_proto.Aggregate.GROUP_TYPE_ROLLUP
                        case "Cube":
                            group_type = snowflake_proto.Aggregate.GROUP_TYPE_CUBE
                        case "GroupingSets":
                            if not exp.userGivenGroupByExprs().isEmpty():
                                raise SnowparkConnectNotImplementedError(
                                    "User-defined group by expressions are not supported"
                                )
                            group_type = (
                                snowflake_proto.Aggregate.GROUP_TYPE_GROUPING_SETS
                            )
                            grouping_sets = [
                                snowflake_proto.Aggregate.GroupingSets(
                                    grouping_set=[
                                        map_logical_plan_expression(e)
                                        for e in as_java_list(grouping_set)
                                    ]
                                )
                                for grouping_set in as_java_list(exp.groupingSets())
                            ]

                if group_type != snowflake_proto.Aggregate.GROUP_TYPE_GROUPBY:
                    if len(group_expression_list) != 1:
                        raise SnowparkConnectNotImplementedError(
                            "Multiple grouping expressions are not supported"
                        )
                    if group_type == snowflake_proto.Aggregate.GROUP_TYPE_GROUPING_SETS:
                        group_expression_list = []  # TODO: exp.userGivenGroupByExprs()?
                    else:
                        group_expression_list = as_java_list(
                            group_expression_list[0].children()
                        )

                grouping_expressions = [
                    map_logical_plan_expression(substitute_lca_in_grouping_expr(e))
                    for e in group_expression_list
                ]

                aggregate_expressions = [
                    map_logical_plan_expression(e)
                    for e in as_java_list(rel.aggregateExpressions())
                ]

                any_proto = Any()
                any_proto.Pack(
                    snowflake_proto.Extension(
                        aggregate=snowflake_proto.Aggregate(
                            input=input,
                            group_type=group_type,
                            grouping_expressions=grouping_expressions,
                            aggregate_expressions=aggregate_expressions,
                            grouping_sets=grouping_sets,
                            having_condition=_having_condition.get(),
                        )
                    )
                )
                proto = relation_proto.Relation(extension=any_proto)
        case "Distinct":
            proto = relation_proto.Relation(
                deduplicate=relation_proto.Deduplicate(
                    input=map_logical_plan_relation(rel.child())
                )
            )
        case "Except":
            proto = relation_proto.Relation(
                set_op=relation_proto.SetOperation(
                    left_input=map_logical_plan_relation(rel.left()),
                    right_input=map_logical_plan_relation(rel.right()),
                    set_op_type=relation_proto.SetOperation.SET_OP_TYPE_EXCEPT,
                    is_all=rel.isAll(),
                )
            )
        case "Filter":
            proto = relation_proto.Relation(
                filter=relation_proto.Filter(
                    input=map_logical_plan_relation(rel.child()),
                    condition=map_logical_plan_expression(rel.condition()),
                )
            )
        case "GlobalLimit":
            # TODO: What's a global limit and what's a local limit?
            proto = map_logical_plan_relation(rel.child())
        case "Intersect":
            proto = relation_proto.Relation(
                set_op=relation_proto.SetOperation(
                    left_input=map_logical_plan_relation(rel.left()),
                    right_input=map_logical_plan_relation(rel.right()),
                    set_op_type=relation_proto.SetOperation.SET_OP_TYPE_INTERSECT,
                    is_all=rel.isAll(),
                )
            )
        case "Join":
            join_type_sql = str(rel.joinType().sql())
            join_type_name = f"JOIN_TYPE_{join_type_sql.replace(' ', '_')}"
            condition = rel.condition()

            left = map_logical_plan_relation(rel.left())
            right = map_logical_plan_relation(rel.right())
            join_condition = (
                map_logical_plan_expression(condition.get())
                if condition.isDefined()
                else None
            )

            if "_NATURAL" in join_type_name:
                join_type_name = join_type_name.replace("_NATURAL", "")
                natural_join_base_offset = NATURAL_JOIN_TYPE_BASE
            else:
                natural_join_base_offset = 0

            if "_USING" in join_type_name:
                using_columns = as_java_list(rel.joinType().usingColumns())
                join_type_name = join_type_name.replace("_USING", "")
            else:
                using_columns = []

            proto = relation_proto.Relation(
                join=relation_proto.Join(
                    left=left,
                    right=right,
                    join_condition=join_condition,
                    join_type=getattr(relation_proto.Join.JoinType, join_type_name)
                    + natural_join_base_offset,
                    using_columns=using_columns,
                )
            )
        case "LocalLimit":

            if rel.limitExpr().getClass().getSimpleName() == "Literal":
                limit_val = rel.limitExpr().value()
            else:
                expr_proto = map_logical_plan_expression(rel.limitExpr())
                session = snowpark.Session.get_active_session()
                m = ColumnNameMap([], [], None)
                expr = map_single_column_expression(
                    expr_proto, m, ExpressionTyper.dummy_typer(session)
                )
                limit_val = session.range(1).select(expr[1].col).collect()[0][0]

            proto = relation_proto.Relation(
                limit=relation_proto.Limit(
                    input=map_logical_plan_relation(rel.child()),
                    limit=limit_val,
                )
            )
        case "Offset":
            proto = relation_proto.Relation(
                offset=relation_proto.Offset(
                    input=map_logical_plan_relation(rel.child()),
                    offset=rel.offsetExpr().value(),
                )
            )
        case "OneRowRelation":
            proto = relation_proto.Relation(project=relation_proto.Project())
        case "Pivot":
            pivot_column = map_logical_plan_expression(rel.pivotColumn())
            session = snowpark.Session.get_active_session()
            m = ColumnNameMap([], [], None)

            pivot_values = [
                map_logical_plan_expression(e) for e in as_java_list(rel.pivotValues())
            ]

            pivot_literals = []

            for expr_proto in pivot_values:
                expr = map_single_column_expression(
                    expr_proto, m, ExpressionTyper.dummy_typer(session)
                )
                value = session.range(1).select(expr[1].col).collect()[0][0]
                pivot_literals.append(
                    expressions_proto.Expression.Literal(string=str(value))
                )

            aggregate_expressions = [
                map_logical_plan_expression(e) for e in as_java_list(rel.aggregates())
            ]

            proto = relation_proto.Relation(
                aggregate=relation_proto.Aggregate(
                    input=map_logical_plan_relation(rel.child()),
                    aggregate_expressions=aggregate_expressions,
                    group_type=relation_proto.Aggregate.GroupType.GROUP_TYPE_PIVOT,
                    pivot=relation_proto.Aggregate.Pivot(
                        col=pivot_column, values=pivot_literals
                    ),
                )
            )

        case "PlanWithUnresolvedIdentifier":
            expr_proto = map_logical_plan_expression(rel.identifierExpr())
            session = snowpark.Session.get_active_session()
            m = ColumnNameMap([], [], None)
            expr = map_single_column_expression(
                expr_proto, m, ExpressionTyper.dummy_typer(session)
            )
            value = session.range(1).select(expr[1].col).collect()[0][0]

            proto = relation_proto.Relation(
                read=relation_proto.Read(
                    named_table=relation_proto.Read.NamedTable(
                        unparsed_identifier=value,
                    )
                )
            )
        case "Project":
            with push_sql_scope():
                input = map_logical_plan_relation(rel.child())
                expressions = [
                    map_logical_plan_expression(e)
                    for e in as_java_list(rel.projectList())
                ]
            proto = relation_proto.Relation(
                project=relation_proto.Project(
                    input=input,
                    expressions=expressions,
                )
            )
        case "Sort":
            proto = relation_proto.Relation(
                sort=relation_proto.Sort(
                    input=map_logical_plan_relation(rel.child()),
                    order=[
                        map_logical_plan_expression(e).sort_order
                        for e in as_java_list(rel.order())
                    ],
                )
            )
        case "SubqueryAlias":
            alias = str(rel.alias())
            proto = relation_proto.Relation(
                subquery_alias=relation_proto.SubqueryAlias(
                    input=map_logical_plan_relation(rel.child()),
                    alias=alias,
                )
            )
            set_sql_plan_name(alias, plan_id)
        case "Union":
            children = as_java_list(rel.children())
            assert len(children) == 2, len(children)

            proto = relation_proto.Relation(
                set_op=relation_proto.SetOperation(
                    left_input=map_logical_plan_relation(children[0]),
                    right_input=map_logical_plan_relation(children[1]),
                    set_op_type=relation_proto.SetOperation.SET_OP_TYPE_UNION,
                    is_all=True,
                    by_name=rel.byName(),
                    allow_missing_columns=rel.allowMissingCol(),
                )
            )
        case "Unpivot":
            value_column_names = [e for e in as_java_list(rel.valueColumnNames())]
            variable_column_name = rel.variableColumnName()

            # Check for multi-column UNPIVOT which Snowflake doesn't support
            if len(value_column_names) > 1:
                raise UnsupportedOperationException(
                    f"Multi-column UNPIVOT is not supported. Snowflake SQL does not support unpivoting "
                    f"multiple value columns ({', '.join(value_column_names)}) in a single operation. "
                    f"Workaround: Use separate UNPIVOT operations for each value column and join the results, "
                    f"or restructure your query to unpivot columns individually."
                )

            values = []
            values_groups = as_java_list(rel.values().get())

            # Check if we have multi-column groups in the IN clause
            if values_groups and len(as_java_list(values_groups[0])) > 1:
                group_sizes = [len(as_java_list(group)) for group in values_groups]
                raise UnsupportedOperationException(
                    f"Multi-column UNPIVOT is not supported. Snowflake SQL does not support unpivoting "
                    f"multiple columns together in groups. Found groups with {max(group_sizes)} columns. "
                    f"Workaround: Unpivot each column separately and then join/union the results as needed."
                )

            for e1 in values_groups:
                for e in as_java_list(e1):
                    values.append(map_logical_plan_expression(e))

            # Need to find ids which are not part of values and remaining cols of df
            input_rel = map_logical_plan_relation(rel.child())
            result = map_relation(input_rel)
            input_df: snowpark.DataFrame = result.dataframe
            column_map = result.column_map
            typer = ExpressionTyper(input_df)
            unpivot_spark_names = []
            for v in values:
                spark_name, typed_column = map_single_column_expression(
                    v, column_map, typer
                )
                unpivot_spark_names.append(spark_name)

            id_cols = []
            for column in input_df.columns:
                spark_column = (
                    column_map.get_spark_column_name_from_snowpark_column_name(column)
                )
                if spark_column not in unpivot_spark_names:
                    id_cols.append(
                        expressions_proto.Expression(
                            unresolved_attribute=expressions_proto.Expression.UnresolvedAttribute(
                                unparsed_identifier=spark_column
                            )
                        )
                    )

            proto = relation_proto.Relation(
                unpivot=relation_proto.Unpivot(
                    input=input_rel,
                    ids=id_cols,
                    values=relation_proto.Unpivot.Values(values=values),
                    variable_column_name=variable_column_name,
                    value_column_name=value_column_names[0],
                )
            )
        case "UnresolvedHaving":
            # Store the having condition in context and process the child aggregate
            child_relation = rel.child()
            if str(child_relation.getClass().getSimpleName()) != "Aggregate":
                raise SnowparkConnectNotImplementedError(
                    "UnresolvedHaving can only be applied to Aggregate relations"
                )

            # Store having condition in a context variable for the Aggregate case to pick up
            having_condition = map_logical_plan_expression(rel.havingCondition())

            # Store in thread-local context (similar to how _ctes works)
            token = _having_condition.set(having_condition)

            try:
                # Recursively call map_logical_plan_relation on the child Aggregate
                # The Aggregate case will pick up the having condition from context
                proto = map_logical_plan_relation(child_relation, plan_id)
            finally:
                _having_condition.reset(token)
        case "UnresolvedHint":
            proto = relation_proto.Relation(
                hint=relation_proto.Hint(
                    input=map_logical_plan_relation(rel.child()),
                    name=str(rel.name()),
                    parameters=[
                        map_logical_plan_expression(e)
                        for e in as_java_list(rel.parameters())
                    ],
                )
            )
        case "UnresolvedInlineTable":
            names = [str(name) for name in as_java_list(rel.names())]
            rows = (
                relation_proto.Relation(
                    common=relation_proto.RelationCommon(
                        plan_id=gen_sql_plan_id(),
                    ),
                    project=relation_proto.Project(
                        expressions=(
                            expressions_proto.Expression(
                                alias=expressions_proto.Expression.Alias(
                                    expr=map_logical_plan_expression(val),
                                    name=[name],
                                )
                            )
                            for name, val in zip(names, as_java_list(row))
                        ),
                    ),
                )
                for row in as_java_list(rel.rows())
            )

            proto = reduce(
                lambda left, right: relation_proto.Relation(
                    common=relation_proto.RelationCommon(
                        plan_id=gen_sql_plan_id(),
                    ),
                    set_op=relation_proto.SetOperation(
                        left_input=left,
                        right_input=right,
                        set_op_type=relation_proto.SetOperation.SET_OP_TYPE_UNION,
                        is_all=True,
                    ),
                ),
                rows,
            )
        case "UnresolvedRelation":
            name = str(rel.name())
            set_sql_plan_name(name, plan_id)

            cte_proto = _ctes.get().get(name)
            if cte_proto is not None:
                # The name corresponds to a `WITH` alias rather than a table.
                # TODO: We currently evaluate the query each time its alias is used;
                # we should eventually start using `WITH` in Snowflake SQL.
                # Each CTE reference should get completely fresh evaluation to prevent ambiguity
                # when the same CTE is joined multiple times. Instead of reusing the same cte_proto,
                # re-evaluate the CTE definition to get fresh column identifiers.

                # Re-evaluate the CTE definition to get fresh column identifiers
                cte_definition = _cte_definitions.get().get(name)
                if cte_definition is not None:
                    # Get the original column names for consistency across CTE references
                    original_container = map_relation(cte_proto)
                    original_spark_columns = (
                        original_container.column_map.get_spark_columns()
                    )

                    # Re-evaluate the CTE definition with a fresh plan_id
                    fresh_plan_id = gen_sql_plan_id()
                    fresh_cte_proto = map_logical_plan_relation(
                        cte_definition, fresh_plan_id
                    )

                    # Use SubqueryColumnAliases to ensure consistent column names across CTE references
                    # This is crucial for CTEs that reference other CTEs
                    any_proto = Any()
                    any_proto.Pack(
                        snowflake_proto.Extension(
                            subquery_column_aliases=snowflake_proto.SubqueryColumnAliases(
                                input=fresh_cte_proto,
                                aliases=original_spark_columns,
                            )
                        )
                    )
                    column_aliased_proto = relation_proto.Relation(extension=any_proto)
                    column_aliased_proto.common.plan_id = gen_sql_plan_id()

                    # Wrap in SubqueryAlias with the CTE name
                    proto = relation_proto.Relation(
                        subquery_alias=relation_proto.SubqueryAlias(
                            input=column_aliased_proto,
                            alias=name,
                        )
                    )
                    proto.common.plan_id = gen_sql_plan_id()
                else:
                    # Fallback to stored CTE if definition not found
                    proto = cte_proto
            else:
                tmp_views = _get_current_temp_objects()
                current_schema = session.connection.schema
                from_table = (
                    CURRENT_CATALOG_NAME,
                    current_schema,
                    name,
                )
                if from_table in tmp_views:
                    _accessing_temp_object.set(True)
                proto = relation_proto.Relation(
                    read=relation_proto.Read(
                        named_table=relation_proto.Read.NamedTable(
                            unparsed_identifier=name,
                        )
                    )
                )
        case "UnresolvedSubqueryColumnAliases":
            child = map_logical_plan_relation(rel.child())
            aliases = [str(a) for a in as_java_list(rel.outputColumnNames())]
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.Extension(
                    subquery_column_aliases=snowflake_proto.SubqueryColumnAliases(
                        input=child,
                        aliases=aliases,
                    )
                )
            )
            proto = relation_proto.Relation(extension=any_proto)
        case "UnresolvedTableValuedFunction":
            name = ".".join(str(part) for part in as_java_list(rel.name())).lower()
            args = [
                map_logical_plan_expression(exp)
                for exp in as_java_list(rel.functionArgs())
            ]

            match name:
                case "range":
                    m = ColumnNameMap([], [], None)
                    session = snowpark.Session.get_active_session()
                    args = (
                        session.range(1)
                        .select(
                            [
                                map_single_column_expression(arg, m, None)[1].col
                                for arg in args
                            ]
                        )
                        .collect()[0]
                    )

                    start, step = 0, 1
                    match args:
                        case [_]:
                            [end] = args
                        case [_, _]:
                            [start, end] = args
                        case [_, _, _]:
                            [start, end, step] = args

                    proto = relation_proto.Relation(
                        range=relation_proto.Range(
                            start=start,
                            end=end,
                            step=step,
                        )
                    )
                case udtf_name if udtf_name in snowpark.Session.get_active_session()._udtfs:
                    # TODO: Table arguments are now expressions, too, so we shouldn't need to handle them here;
                    # instead, handle SubqueryExpression.SUBQUERY_TYPE_TABLE_ARG in relation.map_extension.
                    table_args = []
                    non_table_args = []
                    for i, arg in enumerate(args):
                        extension = snowflake_exp_proto.ExpExtension()
                        if (
                            arg.extension.Unpack(extension)
                            and extension.subquery_expression.subquery_type
                            == snowflake_exp_proto.SubqueryExpression.SUBQUERY_TYPE_TABLE_ARG
                        ):
                            table_args.append(
                                snowflake_proto.TableArgumentInfo(
                                    table_argument=extension.subquery_expression.input,
                                    table_argument_idx=i,
                                )
                            )
                        else:
                            non_table_args.append(arg)

                    if table_args:
                        any_proto = Any()
                        any_proto.Pack(
                            snowflake_proto.Extension(
                                udtf_with_table_arguments=snowflake_proto.UDTFWithTableArguments(
                                    function_name=name,
                                    arguments=non_table_args,
                                    table_arguments=table_args,
                                )
                            )
                        )
                        proto = relation_proto.Relation(extension=any_proto)
                    else:
                        proto = relation_proto.Relation(
                            project=relation_proto.Project(
                                expressions=[
                                    expressions_proto.Expression(
                                        unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                                            function_name=name,
                                            arguments=args,
                                        )
                                    )
                                ],
                            ),
                        )
                case other:
                    proto = relation_proto.Relation(
                        project=relation_proto.Project(
                            expressions=[
                                expressions_proto.Expression(
                                    unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                                        function_name=name,
                                        arguments=args,
                                    )
                                )
                            ],
                        ),
                    )
        case "UnresolvedWith":
            with _push_cte_scope():
                for cte in as_java_list(rel.cteRelations()):
                    name = str(cte._1())
                    # Store the original CTE definition for re-evaluation
                    _cte_definitions.get()[name] = cte._2()
                    # Process CTE definition with a unique plan_id to ensure proper column naming
                    cte_plan_id = gen_sql_plan_id()
                    cte_proto = map_logical_plan_relation(cte._2(), cte_plan_id)
                    _ctes.get()[name] = cte_proto

                proto = map_logical_plan_relation(rel.child())
        case "LateralJoin":
            left = map_logical_plan_relation(rel.left())
            right = map_logical_plan_relation(rel.right().plan())
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.Extension(
                    lateral_join=snowflake_proto.LateralJoin(
                        left=left,
                        right=right,
                    )
                )
            )
            proto = relation_proto.Relation(extension=any_proto)
        case "WithWindowDefinition":
            map_obj = as_java_map(rel.windowDefinitions())
            with _push_window_specs_scope():
                for key, window_spec in map_obj.items():
                    _window_specs.get()[key] = window_spec
                proto = map_logical_plan_relation(rel.child())
        case "Generate":
            # Generate creates a nested Project relation (see lines 1785-1790) without
            # setting its plan_id field. When this Project is later processed by map_project
            # (map_column_ops.py), it uses rel.common.plan_id which defaults to 0 for unset
            # protobuf fields. This means all columns from the Generate operation (both exploded
            # columns and passthrough columns) will have plan_id=0 in their names.
            #
            # If Generate's child is a SubqueryAlias whose inner relation was processed
            # with a non-zero plan_id, there will be a mismatch between:
            # - The columns referenced in the Project (expecting plan_id from SubqueryAlias's child)
            # - The actual column names created by Generate's Project (using plan_id=0)

            # Therefore, when Generate has a SubqueryAlias child, we explicitly process the inner
            # relation with plan_id=0 to match what Generate's Project will use. This only applies when
            # the immediate child of Generate is a SubqueryAlias and preserves existing registrations (like CTEs),
            # so it won't affect other patterns.

            child_class = str(rel.child().getClass().getSimpleName())

            if child_class == "SubqueryAlias":
                alias = str(rel.child().alias())

                # Check if this alias was already registered during initial SQL parsing
                existing_plan_id = get_sql_plan(alias)

                if existing_plan_id is not None:
                    # Use the existing plan_id to maintain consistency with prior registration
                    used_plan_id = existing_plan_id
                else:
                    # Use plan_id=0 to match what the nested Project will use (protobuf default)
                    used_plan_id = 0
                    set_sql_plan_name(alias, used_plan_id)

                # Process the inner child with the determined plan_id
                inner_child = map_logical_plan_relation(
                    rel.child().child(), plan_id=used_plan_id
                )
                input_relation = relation_proto.Relation(
                    subquery_alias=relation_proto.SubqueryAlias(
                        input=inner_child,
                        alias=alias,
                    )
                )
            else:
                input_relation = map_logical_plan_relation(rel.child())
            generator_output_list = as_java_list(rel.generatorOutput())
            generator_output_list_expressions = [
                map_logical_plan_expression(e) for e in generator_output_list
            ]
            qualifier = rel.qualifier().get() if rel.qualifier().isDefined() else None
            function_name = rel.generator().name().toString()
            func_arguments = [
                map_logical_plan_expression(e)
                for e in as_java_list(rel.generator().children())
            ]
            unresolved_fun_proto = expressions_proto.Expression.UnresolvedFunction(
                function_name=function_name, arguments=func_arguments
            )

            aliased_proto = unresolved_fun_proto
            if generator_output_list.size() > 0:
                aliased_proto = expressions_proto.Expression(
                    alias=expressions_proto.Expression.Alias(
                        expr=expressions_proto.Expression(
                            unresolved_function=unresolved_fun_proto,
                        ),
                        name=[attribute.name() for attribute in generator_output_list],
                    )
                )

            # TODO: Fix the bug in snowpark where if we select posexplode with *, it would return columns
            # generated by posexplode two times plus all the other columns
            # Ideal way should have been to do this
            # unresolved_star_expr = expressions_proto.Expression(
            #     unresolved_attribute=expressions_proto.Expression.UnresolvedAttribute(
            #         unparsed_identifier="*",
            #     )
            # )
            # generator_dataframe_proto.project.expressions.append(
            #     unresolved_star_expr
            # )

            # This is a workaround to fix the bug in snowpark where if we select posexplode with *, it would return wrong columns
            input_container = map_relation(input_relation)
            spark_columns = input_container.column_map.get_spark_columns()
            column_expressions = [
                expressions_proto.Expression(
                    unresolved_attribute=expressions_proto.Expression.UnresolvedAttribute(
                        unparsed_identifier=spark_column
                    )
                )
                for spark_column in spark_columns
            ]

            generator_dataframe_proto = relation_proto.Relation(
                project=relation_proto.Project(
                    input=input_relation,
                    expressions=[aliased_proto, *column_expressions],
                )
            )
            if qualifier is not None and qualifier.lower() != "as":
                generator_dataframe_proto = relation_proto.Relation(
                    with_columns=relation_proto.WithColumns(
                        input=generator_dataframe_proto,
                        aliases=[
                            expressions_proto.Expression.Alias(
                                expr=expressions_proto.Expression(
                                    unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                                        function_name="struct",
                                        arguments=generator_output_list_expressions,
                                    )
                                ),
                                name=[qualifier],
                            )
                        ],
                    )
                )
            proto = generator_dataframe_proto
        case other:
            raise SnowparkConnectNotImplementedError(f"Unimplemented relation: {other}")

    proto.common.plan_id = plan_id

    return proto


def _get_relation_identifier(name_obj) -> str:
    # IDENTIFIER(<table_name>), or IDENTIFIER(<method name>)
    expr_proto = map_logical_plan_expression(name_obj.identifierExpr())
    session = snowpark.Session.get_active_session()
    m = ColumnNameMap([], [], None)
    expr = map_single_column_expression(
        expr_proto, m, ExpressionTyper.dummy_typer(session)
    )
    return spark_to_sf_single_id(session.range(1).select(expr[1].col).collect()[0][0])


def get_relation_identifier_name_without_uppercasing(name_obj) -> str:
    if name_obj.getClass().getSimpleName() in (
        "PlanWithUnresolvedIdentifier",
        "ExpressionWithUnresolvedIdentifier",
    ):
        return _get_relation_identifier(name_obj)
    else:
        name = ".".join(
            quote_name_without_upper_casing(str(part))
            for part in as_java_list(name_obj.nameParts())
        )

    return name


def get_relation_identifier_name(name_obj, is_multi_part: bool = False) -> str:
    if name_obj.getClass().getSimpleName() in (
        "PlanWithUnresolvedIdentifier",
        "ExpressionWithUnresolvedIdentifier",
    ):
        return _get_relation_identifier(name_obj)
    else:
        if is_multi_part:
            try:
                # Try multipartIdentifier first for full catalog.database.table
                name = _spark_to_snowflake(name_obj.multipartIdentifier())
            except AttributeError:
                # Fallback to nameParts if multipartIdentifier not available
                name = _spark_to_snowflake(name_obj.nameParts())
        else:
            name = _spark_to_snowflake(name_obj.nameParts())

    return name


def _convert_spark_pattern_to_regex(pattern: str) -> str:
    """
    Convert Spark LIKE pattern to Python regex pattern.

    In Spark LIKE patterns:
    - '*' matches 0 or more characters (equivalent to '.*' in regex)
    - '|' is used to separate multiple patterns (equivalent to '|' in regex)
    - Everything else works like regular regex patterns

    Args:
        pattern: Spark LIKE pattern string

    Returns:
        Python regex pattern string
    """
    if not pattern:
        return ""

    # Split by '|' to handle multiple patterns
    patterns = pattern.split("|")
    regex_patterns = []

    for p in patterns:
        p = p.strip()
        # Replace * with .* for wildcard matching, but preserve other regex characters
        # We need to be careful to only replace standalone * not part of other patterns
        converted = p.replace("*", ".*")
        regex_patterns.append(converted)

    # Join patterns with | for OR matching
    return "|".join(regex_patterns)


def _filter_tables_by_pattern(tables: list, pattern: str) -> list:
    """
    Filter table list by Spark LIKE pattern.

    Args:
        tables: List of table rows from Snowflake SHOW TABLES
        pattern: Spark LIKE pattern

    Returns:
        Filtered list of tables matching the pattern
    """
    if not pattern or not tables:
        return tables

    regex_pattern = _convert_spark_pattern_to_regex(pattern)
    if not regex_pattern:
        return tables

    # Compile regex for case-insensitive matching (as per Spark docs)
    compiled_regex = re.compile(regex_pattern, re.IGNORECASE)

    filtered_tables = []
    for table in tables:
        # Table name is typically the second column in SHOW TABLES output
        table_name = table[1] if len(table) > 1 else str(table[0])
        if compiled_regex.search(table_name):
            filtered_tables.append(table)

    return filtered_tables


def _escape_sql_comment(comment: str) -> str:
    return str(comment).replace("'", "''").replace("\\", "\\\\")
