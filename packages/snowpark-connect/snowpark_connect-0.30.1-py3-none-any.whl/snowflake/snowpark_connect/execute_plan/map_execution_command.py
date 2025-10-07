#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
from collections import Counter

import pyspark.sql.connect.proto.base_pb2 as proto_base
import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake.snowpark.types import StructField, StructType
from snowflake.snowpark_connect.column_name_handler import ColumnNames
from snowflake.snowpark_connect.config import global_config, sessions_config
from snowflake.snowpark_connect.constants import SERVER_SIDE_SESSION_ID
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.execute_plan.utils import pandas_to_arrow_batches_bytes
from snowflake.snowpark_connect.expression import map_udf
from snowflake.snowpark_connect.relation import map_udtf
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.relation.map_sql import map_sql_to_pandas_df
from snowflake.snowpark_connect.relation.write.map_write import map_write, map_write_v2
from snowflake.snowpark_connect.utils.context import get_session_id
from snowflake.snowpark_connect.utils.identifiers import (
    spark_to_sf_single_id,
    spark_to_sf_single_id_with_unquoting,
)
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)
from snowflake.snowpark_connect.utils.temporary_view_cache import register_temp_view


def _create_column_rename_map(
    columns: list[ColumnNames], rename_duplicated: bool
) -> dict:
    if rename_duplicated is False:
        # if we are not renaming duplicated columns, we can just return the original names
        return {
            col.snowpark_name: spark_to_sf_single_id(col.spark_name, is_column=True)
            for col in columns
        }

    column_counts = Counter()
    not_renamed_cols = []
    renamed_cols = []

    for col in columns:
        new_column_name = col.spark_name
        normalized_name = new_column_name.lower()
        column_counts[normalized_name] += 1

        if column_counts[normalized_name] > 1:
            new_column_name = (
                f"{new_column_name}_DEDUP_{column_counts[normalized_name] - 1}"
            )
            renamed_cols.append(ColumnNames(new_column_name, col.snowpark_name, []))
        else:
            not_renamed_cols.append(ColumnNames(new_column_name, col.snowpark_name, []))

    if len(renamed_cols) == 0:
        return {
            col.snowpark_name: spark_to_sf_single_id(col.spark_name, is_column=True)
            for col in not_renamed_cols
        }

    # we need to make sure that we don't have duplicated names after renaming
    # columns that were not renamed in this iteration should have priority over renamed duplicates
    return _create_column_rename_map(not_renamed_cols + renamed_cols, True)


def _find_duplicated_columns(
    columns: list[ColumnNames],
) -> (list[str], list[ColumnNames]):
    duplicates = []
    remaining_columns = []
    seen = set()
    for col in columns:
        if col.spark_name in seen:
            duplicates.append(col.snowpark_name)
        else:
            seen.add(col.spark_name)
            remaining_columns.append(col)
    return duplicates, remaining_columns


def map_execution_command(
    request: proto_base.ExecutePlanRequest,
) -> proto_base.ExecutePlanResponse | None:
    logger.info(request.plan.command.WhichOneof("command_type").upper())
    match request.plan.command.WhichOneof("command_type"):
        case "create_dataframe_view":
            req = request.plan.command.create_dataframe_view
            input_df_container = map_relation(req.input)
            input_df = input_df_container.dataframe
            column_map = input_df_container.column_map

            # TODO: Remove code handling deduplication. When view are not materialized we don't have to care about it.
            session_config = sessions_config[get_session_id()]
            duplicate_column_names_handling_mode = session_config[
                "snowpark.connect.views.duplicate_column_names_handling_mode"
            ]

            spark_columns = input_df_container.column_map.get_spark_columns()
            # rename columns to match spark names
            if duplicate_column_names_handling_mode == "rename":
                # deduplicate column names by appending _DEDUP_1, _DEDUP_2, etc.
                rename_map = _create_column_rename_map(column_map.columns, True)
                snowpark_columns = list(rename_map.values())
                input_df = input_df.rename(rename_map)
            elif duplicate_column_names_handling_mode == "drop":
                # Drop duplicate column names by removing all but the first occurrence.
                duplicated_columns, remaining_columns = _find_duplicated_columns(
                    column_map.columns
                )
                rename_map = _create_column_rename_map(remaining_columns, False)
                snowpark_columns = list(rename_map.values())
                spark_columns = list(dict.fromkeys(spark_columns))
                if len(duplicated_columns) > 0:
                    input_df = input_df.drop(*duplicated_columns)
                input_df = input_df.rename(rename_map)
            else:
                # rename columns without deduplication
                rename_map = _create_column_rename_map(column_map.columns, True)
                snowpark_columns = list(rename_map.values())
                input_df = input_df.rename(rename_map)

            if req.is_global:
                view_name = [global_config.spark_sql_globalTempDatabase, req.name]
            else:
                view_name = [req.name]
            view_name = [
                spark_to_sf_single_id_with_unquoting(part) for part in view_name
            ]
            joined_view_name = ".".join(view_name)

            schema = StructType(
                [
                    StructField(field.name, field.datatype)
                    for field in input_df.schema.fields
                ]
            )
            input_df_container = DataFrameContainer.create_with_column_mapping(
                dataframe=input_df,
                spark_column_names=spark_columns,
                snowpark_column_names=snowpark_columns,
                parent_column_name_map=input_df_container.column_map,
                cached_schema_getter=lambda: schema,
            )

            register_temp_view(joined_view_name, input_df_container, req.replace)
        case "write_stream_operation_start":
            match request.plan.command.write_stream_operation_start.format:
                case "console":
                    # TODO: Make the console output work with Spark style formatting.
                    # result_df: pandas.DataFrame = map_relation(
                    #     relation_proto.Relation(
                    #         show_string=relation_proto.ShowString(
                    #             input=request.plan.command.write_stream_operation_start.input,
                    #             num_rows=100,
                    #             truncate=False,
                    #         )
                    #     )
                    # )
                    # logger.info(result_df.iloc[0, 0])
                    map_relation(
                        request.plan.command.write_stream_operation_start.input
                    ).show()
        case "sql_command":
            sql_command = request.plan.command.sql_command
            pandas_df, schema = map_sql_to_pandas_df(
                sql_command.sql, sql_command.args, sql_command.pos_args
            )
            # SELECT query in SQL command will return None instead of Pandas DF to enable lazy evaluation
            if pandas_df is not None:
                relation = relation_proto.Relation(
                    local_relation=relation_proto.LocalRelation(
                        data=pandas_to_arrow_batches_bytes(pandas_df),
                        schema=schema,
                    )
                )
            else:
                # Return the original SQL query.
                # This is what native Spark Connect does, and the Scala client expects it.
                relation = relation_proto.Relation(
                    sql=relation_proto.SQL(
                        query=sql_command.sql,
                        args=sql_command.args,
                        pos_args=sql_command.pos_args,
                    )
                )
            return proto_base.ExecutePlanResponse(
                session_id=request.session_id,
                operation_id=SERVER_SIDE_SESSION_ID,
                sql_command_result=proto_base.ExecutePlanResponse.SqlCommandResult(
                    relation=relation
                ),
            )
        case "write_operation":
            map_write(request)

        case "write_operation_v2":
            map_write_v2(request)

        case "register_function":
            map_udf.register_udf(request.plan.command.register_function)

        case "register_table_function":
            map_udtf.register_udtf(request.plan.command.register_table_function)

        case other:
            raise SnowparkConnectNotImplementedError(
                f"Command type {other} not implemented"
            )
