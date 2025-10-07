#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import base64
import inspect
import json
import sys
from typing import NamedTuple, Optional

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
from pyspark.errors.exceptions.base import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
import snowflake.snowpark_connect.tcm as tcm
import snowflake.snowpark_connect.utils.udf_utils as udf_utils
from snowflake.snowpark import Column, Session
from snowflake.snowpark.types import DataType, _parse_datatype_json_value
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.utils.context import (
    get_is_aggregate_function,
    get_is_evaluating_join_condition,
)
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger

CREATE_UDF_SPROC_NAME_PREFIX = "__SC_BUILD_IN_CREATE_UDF"
TEST_FLAG_FORCE_CREATE_SPROC = False


class SnowparkUDF(NamedTuple):
    name: str
    return_type: DataType
    input_types: list[DataType]
    original_return_type: DataType | None


def require_creating_udf_in_sproc(
    udf_proto: expressions_proto.CommonInlineUserDefinedFunction,
) -> bool:
    """
    If a python UDF's python version does not match with current runtime, create it in a sproc using that python version.
    """
    return (
        TEST_FLAG_FORCE_CREATE_SPROC
        or tcm.TCM_MODE
        or (
            udf_proto.WhichOneof("function") == "python_udf"
            and udf_proto.python_udf.python_ver is not None
            and f"{sys.version_info.major}.{sys.version_info.minor}"
            != udf_proto.python_udf.python_ver
        )
    )


def process_udf_in_sproc(
    common_inline_user_defined_function: expressions_proto.CommonInlineUserDefinedFunction,
    called_from: str,
    return_type: DataType,
    input_types: list | None = None,
    input_column_names: list[str] | None = None,
    udf_name: str | None = None,
    replace: bool = False,
    udf_packages: str = "",
    udf_imports: str = "",
    original_return_type: DataType | None = None,
) -> SnowparkUDF:
    """Helper method to call the sproc to create inline UDF and return the essential info of the UDF."""
    session = get_or_create_snowpark_session()
    sproc_name = _get_or_create_udf_sproc_helper(
        session,
        common_inline_user_defined_function.python_udf.python_ver,
    )
    udf_proto_encoded = base64.b64encode(
        common_inline_user_defined_function.SerializeToString()
    ).decode("ascii")

    def gen_input_types_json_str(input_types: list | None = None) -> Optional[str]:
        if input_types is None:
            return None
        return json.dumps([dt.json_value() for dt in input_types])

    input_types_json_str = gen_input_types_json_str(input_types)

    input_column_names_json_str = (
        None if input_column_names is None else json.dumps(input_column_names)
    )

    original_return_type_json_str = (
        None
        if original_return_type is None
        else json.dumps(original_return_type.json_value())
    )

    sproc_res = session.call(
        sproc_name,
        called_from,
        json.dumps(return_type.json_value()),
        input_types_json_str,
        input_column_names_json_str,
        snowpark_fn.lit(udf_name),
        replace,
        udf_packages,
        udf_imports,
        udf_proto_encoded,
        original_return_type_json_str,
    )

    udf_attr = json.loads(sproc_res)
    snowpark_udf = SnowparkUDF(
        name=udf_attr["name"],
        input_types=[_parse_datatype_json_value(t) for t in udf_attr["input_types"]],
        return_type=_parse_datatype_json_value(udf_attr["return_type"]),
        original_return_type=original_return_type,
    )
    if called_from == "register_udf":
        session._udfs[
            common_inline_user_defined_function.function_name.lower()
        ] = snowpark_udf
    return snowpark_udf


def _get_or_create_udf_sproc_helper(
    session: Session,
    python_version: str = f"{sys.version_info.major}.{sys.version_info.minor}",
) -> str:
    """
    This helper method will get or create a sproc in targeted python version to create the python UDF. The sproc's
    return value is a json string containing the UDF's name, input types, and, return type.
    """
    sproc_name = f"{CREATE_UDF_SPROC_NAME_PREFIX}_{python_version.replace('.', '_')}"
    if sproc_name in session._sprocs:
        return sproc_name

    inline_udf_utils_py_code = inspect.getsource(udf_utils)

    create_udf_sproc_sql = f"""
CREATE OR REPLACE TEMPORARY PROCEDURE {sproc_name}(
    called_from VARCHAR,
    return_type_json_str VARCHAR,
    input_types_json_str VARCHAR,
    input_column_names_json_str VARCHAR,
    udf_name VARCHAR,
    replace BOOLEAN,
    udf_packages VARCHAR,
    udf_imports VARCHAR,
    base64_str VARCHAR,
    original_return_type VARCHAR
)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '{python_version}'
PACKAGES = ('pyspark>=3.5.0,<4', 'cloudpickle', 'snowflake-snowpark-python==1.32.0', 'grpcio>=1.48.1')
HANDLER = 'create'
EXECUTE AS CALLER
AS $$
import cloudpickle
import base64
from pyspark.sql.connect.proto.expressions_pb2 import CommonInlineUserDefinedFunction
import json
from snowflake.snowpark.types import *
from typing import Optional
from snowflake.snowpark.types import _parse_datatype_json_value

{inline_udf_utils_py_code}

def parse_input_types(input_types_json_str) -> Optional[list[DataType]]:
    if input_types_json_str is None:
        return None
    input_types_json = json.loads(input_types_json_str)
    return [_parse_datatype_json_value(t) for t in input_types_json]

def parse_return_type(return_type_json_str) -> Optional[DataType]:
    return_type_json = json.loads(return_type_json_str)
    result = _parse_datatype_json_value(return_type_json)
    if isinstance(result, (ArrayType, MapType, StructType)):
        result = result._as_nested()
    return result


def create(session, called_from, return_type_json_str, input_types_json_str, input_column_names_json_str, udf_name, replace, udf_packages, udf_imports, b64_str, original_return_type):
    import snowflake.snowpark.context as context
    context._use_structured_type_semantics = True
    context._is_snowpark_connect_compatible_mode = True

    restored_bytes = base64.b64decode(b64_str.encode('ascii'))
    udf_proto = CommonInlineUserDefinedFunction()
    udf_proto.ParseFromString(restored_bytes)
    udf_processor = ProcessCommonInlineUserDefinedFunction(
        udf_proto,
        input_types=parse_input_types(input_types_json_str),
        return_type=parse_return_type(return_type_json_str),
        called_from=called_from,
        input_column_names=None if input_column_names_json_str is None else json.loads(input_column_names_json_str),
        udf_name=udf_name,
        replace=replace,
        udf_packages=udf_packages,
        udf_imports=udf_imports,
        original_return_type=parse_return_type(original_return_type) if original_return_type else None,
    )
    udf = udf_processor.create_udf()
    return json.dumps({{"name": udf.name, "return_type": udf._return_type.json_value(), "input_types": [t.json_value() for t in udf._input_types]}})
$$;
"""
    session.sql(create_udf_sproc_sql).collect()
    session._sprocs.add(sproc_name)
    logger.info(f"Procedure {sproc_name} created")
    return sproc_name


def udf_check(
    udf_proto: expressions_proto.CommonInlineUserDefinedFunction,
) -> None:
    _check_supported_udf(udf_proto)
    _aggregate_function_check(udf_proto)


def _check_supported_udf(
    udf_proto: expressions_proto.CommonInlineUserDefinedFunction,
) -> None:
    match udf_proto.WhichOneof("function"):
        case "python_udf":
            pass
        case "java_udf":
            from snowflake.snowpark_connect.utils.session import (
                get_or_create_snowpark_session,
            )

            session = get_or_create_snowpark_session()
            if udf_proto.java_udf.class_name not in session._cached_java_udfs:
                raise AnalysisException(
                    f"Can not load class {udf_proto.java_udf.class_name}"
                )
            else:
                raise ValueError(
                    "Function type java_udf not supported for common inline user-defined function"
                )
        case "scalar_scala_udf":
            pass
        case _ as function_type:
            raise ValueError(
                f"Function type {function_type} not supported for common inline user-defined function"
            )


def _aggregate_function_check(
    udf_proto: expressions_proto.CommonInlineUserDefinedFunction,
):
    name, is_aggregate_function = get_is_aggregate_function()
    if not udf_proto.deterministic and name != "default" and is_aggregate_function:
        raise AnalysisException(
            f"[AGGREGATE_FUNCTION_WITH_NONDETERMINISTIC_EXPRESSION] Non-deterministic expression {name}({udf_proto.function_name}) should not appear in the arguments of an aggregate function."
        )


def _join_checks(snowpark_udf_arg_names: list[str]):
    is_evaluating_join_condition = get_is_evaluating_join_condition()
    is_left_evaluable, is_right_evaluable = False, False

    for snowpark_udf_arg_name in snowpark_udf_arg_names:
        # UDFs can only reference EITHER the left OR the right side of the join but not both.
        # Example: Assume left has column a and right has column b.
        # lambda a: str(a) is fine because it will only reference either the left dataframe or the right dataframe.
        # lambda a, b: a == b is not fine because it will reference both of the dataframes.
        is_left_evaluable = (
            is_left_evaluable
            or snowpark_udf_arg_name in is_evaluating_join_condition[2]
        )
        is_right_evaluable = (
            is_right_evaluable
            or snowpark_udf_arg_name in is_evaluating_join_condition[3]
        )
        # Check for implicit cartesian product only on inner joins. If crossjoin is disabled, raise an exception.
        if (
            is_evaluating_join_condition[0] == "INNER"
            and not global_config.spark_sql_crossJoin_enabled
            and is_left_evaluable
            and is_right_evaluable
        ):
            raise AnalysisException(
                f"Detected implicit cartesian product for {is_evaluating_join_condition[0]} join between logical plans. \n"
                f"Join condition is missing or trivial. \n"
                f"Either: use the CROSS JOIN syntax to allow cartesian products between those relations, or; "
                f"enable implicit cartesian products by setting the configuration variable spark.sql.crossJoin.enabled=True."
            )
        if (
            is_evaluating_join_condition[0] != "INNER"
            and is_evaluating_join_condition[1]
            and is_left_evaluable
            and is_right_evaluable
        ):
            raise AnalysisException(
                f"[UNSUPPORTED_FEATURE.PYTHON_UDF_IN_ON_CLAUSE] The feature is not supported: "
                f"Python UDF in the ON clause of a {is_evaluating_join_condition[0]} JOIN. "
                f"In case of an INNNER JOIN consider rewriting to a CROSS JOIN with a WHERE clause."
            )


def infer_snowpark_arguments(
    udf_proto: expressions_proto.CommonInlineUserDefinedFunction,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[list[str], list[Column]]:
    snowpark_udf_args: list[Column] = []
    snowpark_udf_arg_names: list[str] = []
    for arg_exp in udf_proto.arguments:
        (
            snowpark_udf_arg_name,
            snowpark_udf_arg,
        ) = map_single_column_expression(arg_exp, column_mapping, typer)
        snowpark_udf_arg = snowpark_udf_arg.col
        snowpark_udf_args.append(snowpark_udf_arg)
        snowpark_udf_arg_names.append(snowpark_udf_arg_name)
    _join_checks(snowpark_udf_arg_names)
    return snowpark_udf_arg_names, snowpark_udf_args


def gen_input_types(
    snowpark_udf_args: list[Column],
    typer: ExpressionTyper,
):
    input_types = []
    for udf_arg in snowpark_udf_args:
        input_types.extend(typer.type(udf_arg))
    return input_types
