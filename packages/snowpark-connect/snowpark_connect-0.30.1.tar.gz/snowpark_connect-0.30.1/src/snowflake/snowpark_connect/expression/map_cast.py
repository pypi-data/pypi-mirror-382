#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
import pyspark.sql.connect.proto.types_pb2 as types_proto
from pyspark.errors.exceptions.base import (
    AnalysisException,
    NumberFormatException,
    SparkRuntimeException,
)

import snowflake.snowpark.functions as snowpark_fn
from snowflake.snowpark.types import (
    BinaryType,
    BooleanType,
    DataType,
    DateType,
    DoubleType,
    IntegerType,
    LongType,
    MapType,
    NullType,
    StringType,
    StructType,
    TimestampTimeZone,
    TimestampType,
    _FractionalType,
    _IntegralType,
    _NumericType,
)
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.type_mapping import (
    map_type_string_to_snowpark_type,
    proto_to_snowpark_type,
    snowpark_to_proto_type,
)
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    get_is_evaluating_sql,
    is_function_argument_being_resolved,
)
from snowflake.snowpark_connect.utils.udf_cache import cached_udf

SYMBOL_FUNCTIONS = {"<", ">", "<=", ">=", "!=", "+", "-", "*", "/", "%", "div"}

CAST_FUNCTIONS = {
    "boolean": types_proto.DataType(boolean=types_proto.DataType.Boolean()),
    "int": types_proto.DataType(integer=types_proto.DataType.Integer()),
    "smallint": types_proto.DataType(integer=types_proto.DataType.Integer()),
    "bigint": types_proto.DataType(long=types_proto.DataType.Long()),
    "tinyint": types_proto.DataType(byte=types_proto.DataType.Byte()),
    "float": types_proto.DataType(float=types_proto.DataType.Float()),
    "double": types_proto.DataType(double=types_proto.DataType.Double()),
    "string": types_proto.DataType(string=types_proto.DataType.String()),
    "decimal": types_proto.DataType(
        decimal=types_proto.DataType.Decimal(precision=10, scale=0)
    ),
    "date": types_proto.DataType(date=types_proto.DataType.Date()),
    "timestamp": types_proto.DataType(timestamp=types_proto.DataType.Timestamp()),
    "binary": types_proto.DataType(binary=types_proto.DataType.Binary()),
}


def map_cast(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
    from_type_cast: bool = False,
) -> tuple[list[str], TypedColumn]:
    """
    Map a cast expression to a Snowpark expression.
    """
    from snowflake.snowpark_connect.expression.map_expression import (
        map_single_column_expression,
    )

    spark_sql_ansi_enabled = global_config.spark_sql_ansi_enabled

    match exp.cast.WhichOneof("cast_to_type"):
        case "type":
            to_type = proto_to_snowpark_type(exp.cast.type)
            to_type_str = to_type.simpleString().upper()
        case "type_str":
            to_type = map_type_string_to_snowpark_type(exp.cast.type_str)
            to_type_str = exp.cast.type_str.upper()
        case _:
            raise ValueError("No type to cast to")

    from_exp = exp.cast.expr
    new_name, typed_column = map_single_column_expression(
        from_exp, column_mapping, typer
    )

    match from_exp.WhichOneof("expr_type"):
        case "unresolved_attribute" if not is_function_argument_being_resolved():
            col_name = new_name
        case "literal" if not is_function_argument_being_resolved() and from_type_cast:
            col_name = new_name
        case "unresolved_function" if from_exp.unresolved_function.function_name in SYMBOL_FUNCTIONS:
            col_name = new_name
        case _ if to_type.typeName().upper() in ("STRUCT", "ARRAY"):
            col_name = new_name
        case _ if get_is_evaluating_sql():
            col_name = f"CAST({new_name} AS {to_type_str})"
        case _:
            col_name = new_name

    from_type = typed_column.typ

    if from_exp.WhichOneof("expr_type") == "literal":
        if (
            spark_sql_ansi_enabled
            and not isinstance(from_type, NullType)
            and (
                isinstance(to_type, _NumericType)
                or isinstance(to_type, BinaryType)
                or isinstance(to_type, BooleanType)
            )
        ):
            sanity_check(to_type, new_name, from_type, from_type_cast)

    col = typed_column.col
    # On TCM, sometimes these are StringType(x)
    # This normalizes them for the cast.
    if isinstance(from_type, StringType):
        from_type = StringType()
    if isinstance(to_type, StringType):
        to_type = StringType()

    match (from_type, to_type):
        case (_, _) if (from_type == to_type):
            result_exp = col
        case (NullType(), _):
            result_exp = col.cast(to_type)
        case (StructType(), _) if from_type.structured:
            result_exp = col.cast(to_type, rename_fields=True)
        case (MapType(), StringType()):

            def _map_to_string(map: dict) -> str:
                def format_value(v):
                    if isinstance(v, dict):
                        return _map_to_string(v)
                    elif isinstance(v, list):
                        return "[" + ", ".join(format_value(item) for item in v) + "]"
                    elif isinstance(v, bool):
                        return str(v).lower()  # Spark prints true/false
                    elif v is None:
                        return "null"
                    else:
                        return str(v)

                if map is None:
                    return None
                parts = [f"{k} -> {format_value(v)}" for k, v in map.items()]
                return "{" + ", ".join(parts) + "}"

            _map_entries = cached_udf(
                _map_to_string,
                input_types=[StructType()],
                return_type=StringType(),
            )

            result_exp = snowpark_fn.cast(
                _map_entries(col.cast(StructType())),
                StringType(),
            )

        # date and timestamp
        case (TimestampType(), _) if isinstance(to_type, _NumericType):
            epoch_s = snowpark_fn.date_part("epoch_seconds", col)
            result_exp = epoch_s.cast(to_type)
        case (TimestampType(), BooleanType()):
            timestamp_0L = snowpark_fn.to_timestamp(snowpark_fn.lit(0))
            result_exp = snowpark_fn.when(
                col.is_not_null(),
                col
                != timestamp_0L,  # 0L timestamp is mapped to False, other values are mapped to True
            ).otherwise(snowpark_fn.lit(None))
        case (TimestampType(), DateType()):
            result_exp = snowpark_fn.to_date(col)
        case (DateType(), TimestampType()):
            result_exp = snowpark_fn.to_timestamp(col)
            result_exp = result_exp.cast(TimestampType(TimestampTimeZone.NTZ))
        case (TimestampType() as f, TimestampType() as t) if f.tzinfo == t.tzinfo:
            result_exp = col
        case (
            TimestampType(),
            TimestampType() as t,
        ) if t.tzinfo == TimestampTimeZone.NTZ:
            zone = global_config.spark_sql_session_timeZone
            result_exp = snowpark_fn.convert_timezone(snowpark_fn.lit(zone), col).cast(
                TimestampType(TimestampTimeZone.NTZ)
            )
        case (TimestampType(), TimestampType()):
            result_exp = col.cast(to_type)
        case (_, TimestampType()) if isinstance(from_type, _NumericType):
            microseconds = col * snowpark_fn.lit(1000000)
            result_exp = snowpark_fn.when(
                col < 0, snowpark_fn.ceil(microseconds)
            ).otherwise(snowpark_fn.floor(microseconds))
            result_exp = result_exp.cast(LongType())
            result_exp = snowpark_fn.to_timestamp(
                result_exp, snowpark_fn.lit(6)
            )  # microseconds precision
            result_exp = result_exp.cast(TimestampType(TimestampTimeZone.NTZ))
        case (_, TimestampType()) if isinstance(from_type, BooleanType):
            result_exp = snowpark_fn.to_timestamp(
                col.cast(LongType()), snowpark_fn.lit(6)
            )  # microseconds precision
            result_exp = result_exp.cast(TimestampType(TimestampTimeZone.NTZ))
        case (_, TimestampType()):
            if spark_sql_ansi_enabled:
                result_exp = snowpark_fn.to_timestamp(col)
            else:
                result_exp = snowpark_fn.function("try_to_timestamp")(col)
            result_exp = result_exp.cast(TimestampType(TimestampTimeZone.NTZ))
        case (DateType(), _) if isinstance(to_type, (_NumericType, BooleanType)):
            result_exp = snowpark_fn.cast(snowpark_fn.lit(None), to_type)
        case (_, DateType()):
            if spark_sql_ansi_enabled:
                result_exp = snowpark_fn.to_date(col)
            else:
                result_exp = snowpark_fn.function("try_to_date")(col)
        # boolean
        case (BooleanType(), _) if isinstance(to_type, _NumericType):
            result_exp = col.cast(LongType()).cast(to_type)
        case (_, BooleanType()) if isinstance(from_type, _NumericType):
            result_exp = col.cast(LongType()).cast(to_type)

        # binary
        case (StringType(), BinaryType()):
            result_exp = snowpark_fn.to_binary(col, "UTF-8")
        case (_IntegralType(), BinaryType()):
            type_name = type(from_type).__name__.lower().replace("type", "")
            match type_name:
                case "byte":
                    digits = 2
                case "short":
                    digits = 4
                case "integer":
                    digits = 8
                case _:
                    # default to long
                    digits = 16

            result_exp = snowpark_fn.when(
                col.isNull(), snowpark_fn.lit(None)
            ).otherwise(
                snowpark_fn.to_binary(
                    snowpark_fn.lpad(
                        snowpark_fn.ltrim(
                            snowpark_fn.to_char(col, snowpark_fn.lit("X" * digits))
                        ),
                        snowpark_fn.lit(digits),
                        snowpark_fn.lit("0"),
                    )
                )
            )
        case (_, BinaryType()):
            result_exp = snowpark_fn.try_to_binary(col)
        case (BinaryType(), StringType()):
            result_exp = snowpark_fn.to_varchar(col, "UTF-8")

        # numeric
        case (_, _) if isinstance(from_type, _FractionalType) and isinstance(
            to_type, _IntegralType
        ):
            result_exp = (
                snowpark_fn.when(
                    col == snowpark_fn.lit(float("nan")), snowpark_fn.lit(0)
                )
                .when(col < 0, snowpark_fn.ceil(col))
                .otherwise(snowpark_fn.floor(col))
            )
            result_exp = result_exp.cast(to_type)
        case (StringType(), _) if (isinstance(to_type, _IntegralType)):
            if spark_sql_ansi_enabled:
                result_exp = snowpark_fn.cast(col, DoubleType())
            else:
                result_exp = snowpark_fn.try_cast(col, DoubleType())
            result_exp = snowpark_fn.when(
                result_exp < 0, snowpark_fn.ceil(result_exp)
            ).otherwise(snowpark_fn.floor(result_exp))
            result_exp = result_exp.cast(to_type)
        # https://docs.snowflake.com/en/sql-reference/functions/try_cast Only works on certain types (mostly non-structured ones)
        case (StringType(), _) if isinstance(to_type, _NumericType) or isinstance(
            to_type, StringType
        ) or isinstance(to_type, BooleanType) or isinstance(
            to_type, DateType
        ) or isinstance(
            to_type, TimestampType
        ) or isinstance(
            to_type, BinaryType
        ):
            if spark_sql_ansi_enabled:
                result_exp = snowpark_fn.cast(col, to_type)
            else:
                result_exp = snowpark_fn.try_cast(col, to_type)
        case (StringType(), _):
            raise AnalysisException(
                f"""[DATATYPE_MISMATCH.CAST_WITHOUT_SUGGESTION] Cannot resolve "{col_name}" due to data type mismatch: cannot cast "{snowpark_to_proto_type(from_type, column_mapping)}" to "{exp.cast.type_str.upper()}".;"""
            )
        case _:
            result_exp = snowpark_fn.cast(col, to_type)

    return [col_name], TypedColumn(result_exp, lambda: [to_type])


def sanity_check(
    to_type: DataType, value: str, from_type: DataType, from_type_cast: bool
) -> None:
    """
    This is a basic validation to ensure the casting is legal.
    """

    if isinstance(from_type, LongType) and isinstance(to_type, BinaryType):
        raise NumberFormatException(
            f"""[DATATYPE_MISMATCH.CAST_WITH_CONF_SUGGESTION] Cannot resolve "CAST({value} AS BINARY)" due to data type mismatch: cannot cast "BIGINT" to "BINARY" with ANSI mode on."""
        )

    if (
        from_type_cast
        and isinstance(from_type, StringType)
        and isinstance(to_type, BooleanType)
    ):
        if value is not None:
            value = value.strip().lower()
        if value not in {"t", "true", "f", "false", "y", "yes", "n", "no", "0", "1"}:
            raise SparkRuntimeException(
                f"""[CAST_INVALID_INPUT] The value '{value}' of the type "STRING" cannot be cast to "BOOLEAN" because it is malformed. Correct the value as per the syntax, or change its target type. Use `try_cast` to tolerate malformed input and return NULL instead. If necessary set "spark.sql.ansi.enabled" to "false" to bypass this error."""
            )

    raise_cast_failure_exception = False
    if isinstance(to_type, _IntegralType):
        try:
            x = int(value)
            if isinstance(to_type, IntegerType) and (x > 2147483647 or x < -2147483648):
                raise_cast_failure_exception = True
            elif isinstance(to_type, LongType) and (
                x > 9223372036854775807 or x < -9223372036854775808
            ):
                raise_cast_failure_exception = True
        except Exception:
            raise_cast_failure_exception = True
    elif isinstance(to_type, _FractionalType):
        try:
            float(value)
        except Exception:
            raise_cast_failure_exception = True
    if raise_cast_failure_exception:
        raise NumberFormatException(
            """[CAST_INVALID_INPUT] Correct the value as per the syntax, or change its target type. Use `try_cast` to tolerate malformed input and return NULL instead. If necessary setting "spark.sql.ansi.enabled" to "false" may bypass this error."""
        )
