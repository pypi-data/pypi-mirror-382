#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.sql.connect.proto.expressions_pb2 import CommonInlineUserDefinedFunction

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark.types import StructType
from snowflake.snowpark_connect.constants import MAP_IN_ARROW_EVAL_TYPE
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.type_mapping import proto_to_snowpark_type
from snowflake.snowpark_connect.utils.pandas_udtf_utils import (
    create_pandas_udtf,
    create_pandas_udtf_with_arrow,
)
from snowflake.snowpark_connect.utils.udf_helper import udf_check
from snowflake.snowpark_connect.utils.udtf_helper import (
    create_pandas_udtf_in_sproc,
    require_creating_udtf_in_sproc,
)


def map_map_partitions(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Map a function over the partitions of the input DataFrame.

    This is a simple wrapper around the `mapInPandas` method in Snowpark.
    """
    input_container = map_relation(rel.map_partitions.input)
    udf_proto = rel.map_partitions.func
    udf_check(udf_proto)

    return _map_with_pandas_udtf(input_container, udf_proto)


def _call_udtf(
    udtf_name: str, input_df: snowpark.DataFrame, return_type: StructType | None = None
) -> snowpark.DataFrame:
    # Add a dummy column with random 1-10 values for partitioning
    input_df_with_dummy = input_df.withColumn(
        "_DUMMY_PARTITION_KEY",
        (
            snowpark_fn.uniform(
                snowpark_fn.lit(1), snowpark_fn.lit(10), snowpark_fn.random()
            )
            * 10
        ).cast("int"),
    )

    udtf_columns = [f"snowflake_jtf_{column}" for column in input_df.columns] + [
        "_DUMMY_PARTITION_KEY"
    ]

    tfc = snowpark_fn.call_table_function(udtf_name, *udtf_columns).over(
        partition_by=[snowpark_fn.col("_DUMMY_PARTITION_KEY")]
    )

    # Overwrite the input_df columns to prevent name conflicts with UDTF output columns
    result_df_with_dummy = input_df_with_dummy.to_df(udtf_columns).join_table_function(
        tfc
    )

    output_cols = [field.name for field in return_type.fields]

    # Only return the output columns.
    result_df = result_df_with_dummy.select(*output_cols)

    return DataFrameContainer.create_with_column_mapping(
        dataframe=result_df,
        spark_column_names=output_cols,
        snowpark_column_names=output_cols,
        snowpark_column_types=[field.datatype for field in return_type.fields],
    )


def _map_with_pandas_udtf(
    input_df_container: DataFrameContainer,
    udf_proto: CommonInlineUserDefinedFunction,
) -> snowpark.DataFrame:
    """
    Handle mapInArrow using pandas_udtf for partition-level Arrow processing.
    """
    input_df = input_df_container.dataframe
    input_schema = input_df.schema
    spark_column_names = input_df_container.column_map.get_spark_columns()
    return_type = proto_to_snowpark_type(
        udf_proto.python_udf.output_type
        if udf_proto.WhichOneof("function") == "python_udf"
        else udf_proto.scalar_scala_udf.outputType
    )

    # Check if this is mapInArrow (eval_type == 207)
    map_in_arrow = (
        udf_proto.WhichOneof("function") == "python_udf"
        and udf_proto.python_udf.eval_type == MAP_IN_ARROW_EVAL_TYPE
    )
    if require_creating_udtf_in_sproc(udf_proto):
        udtf_name = create_pandas_udtf_in_sproc(
            udf_proto, spark_column_names, input_schema, return_type
        )
    else:
        if map_in_arrow:
            map_udtf = create_pandas_udtf_with_arrow(
                udf_proto, spark_column_names, input_schema, return_type
            )
        else:
            map_udtf = create_pandas_udtf(
                udf_proto, spark_column_names, input_schema, return_type
            )
        udtf_name = map_udtf.name
    return _call_udtf(udtf_name, input_df, return_type)
