#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

"""
Spark error references:
https://github.com/apache/spark/blob/master/docs/sql-error-conditions.md
https://github.com/apache/spark/tree/master/sql/catalyst/src/main/scala/org/apache/spark/sql/errors
https://github.com/apache/spark/blob/master/common/utils/src/main/resources/error/error-conditions.json
"""

import json
import pathlib
import re
import traceback

import jpype
from google.protobuf import any_pb2
from google.rpc import code_pb2, error_details_pb2, status_pb2
from pyspark.errors.error_classes import ERROR_CLASSES_MAP
from pyspark.errors.exceptions.base import (
    AnalysisException,
    ArithmeticException,
    ArrayIndexOutOfBoundsException,
    IllegalArgumentException,
    NumberFormatException,
    ParseException,
    PySparkException,
    PythonException,
    SparkRuntimeException,
    UnsupportedOperationException,
)
from pyspark.errors.exceptions.connect import SparkConnectGrpcException
from snowflake.core.exceptions import NotFoundError

from snowflake.connector.errors import ProgrammingError
from snowflake.snowpark.exceptions import SnowparkClientException, SnowparkSQLException
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.error.error_mapping import ERROR_MAPPINGS_JSON

# The JSON string in error_mapping.py is a copy of https://github.com/apache/spark/blob/master/common/utils/src/main/resources/error/error-conditions.json.
# The file doesn't have to be synced with spark latest main. Just update it when required.
current_dir = pathlib.Path(__file__).parent.resolve()
ERROR_CLASSES_MAP.update(json.loads(ERROR_MAPPINGS_JSON))

SPARK_PYTHON_TO_JAVA_EXCEPTION = {
    AnalysisException: "org.apache.spark.sql.AnalysisException",
    ParseException: "org.apache.spark.sql.catalyst.parser.ParseException",
    IllegalArgumentException: "java.lang.IllegalArgumentException",
    ArithmeticException: "java.lang.ArithmeticException",
    ArrayIndexOutOfBoundsException: "java.lang.ArrayIndexOutOfBoundsException",
    NumberFormatException: "java.lang.NumberFormatException",
    SparkRuntimeException: "org.apache.spark.SparkRuntimeException",
    SparkConnectGrpcException: "pyspark.errors.exceptions.connect.SparkConnectGrpcException",
    PythonException: "org.apache.spark.api.python.PythonException",
    UnsupportedOperationException: "java.lang.UnsupportedOperationException",
}

WINDOW_FUNCTION_ANALYSIS_EXCEPTION_SQL_ERROR_CODE = {1005, 2303}
ANALYSIS_EXCEPTION_SQL_ERROR_CODE = {
    904,
    1039,
    1044,
    2002,
    *WINDOW_FUNCTION_ANALYSIS_EXCEPTION_SQL_ERROR_CODE,
}

# utdf related error messages
init_multi_args_exception_pattern = (
    r"__init__\(\) missing \d+ required positional argument"
)
terminate_multi_args_exception_pattern = (
    r"terminate\(\) missing \d+ required positional argument"
)
snowpark_connect_exception_pattern = re.compile(
    r"\[snowpark-connect-exception(?::(\w+))?\]\s*(.+?)'\s*is not recognized"
)
invalid_bit_pattern = re.compile(
    r"Invalid bit position: \d+ exceeds the bit (?:upper|lower) limit",
    re.IGNORECASE,
)


def contains_udtf_select(sql_string):
    # This function tries to detect if the SQL string contains a UDTF (User Defined Table Function) call.
    # Looks for select FROM TABLE(...) or FROM ( TABLE(...) )
    return bool(
        re.search(
            r"select\s+.*from\s+\(?\s*table\s*\(", sql_string, re.IGNORECASE | re.DOTALL
        )
    )


def _get_converted_known_sql_or_custom_exception(
    ex: Exception,
) -> Exception | None:
    # Use lower-case for case-insensitive matching
    msg = ex.message.lower() if hasattr(ex, "message") else str(ex).lower()
    query = ex.query if hasattr(ex, "query") else ""

    # custom exception
    if "[snowpark_connect::invalid_array_index]" in msg:
        return ArrayIndexOutOfBoundsException(
            message='The index <indexValue> is out of bounds. The array has <arraySize> elements. Use the SQL function `get()` to tolerate accessing element at invalid index and return NULL instead. If necessary set "spark.sql.ansi.enabled" to "false" to bypass this error.'
        )
    if "[snowpark_connect::invalid_index_of_zero]" in msg:
        return SparkRuntimeException(
            message="[INVALID_INDEX_OF_ZERO] The index 0 is invalid. An index shall be either < 0 or > 0 (the first element has index 1)."
        )
    if "[snowpark_connect::invalid_index_of_zero_in_slice]" in msg:
        return SparkRuntimeException(
            message="Unexpected value for start in function slice: SQL array indices start at 1."
        )
    invalid_bit = invalid_bit_pattern.search(msg)
    if invalid_bit:
        return IllegalArgumentException(message=invalid_bit.group(0))
    match = snowpark_connect_exception_pattern.search(
        ex.message if hasattr(ex, "message") else str(ex)
    )
    if match:
        class_name = match.group(1)
        message = match.group(2)
        exception_class = (
            globals().get(class_name, SparkConnectGrpcException)
            if class_name
            else SparkConnectGrpcException
        )
        return exception_class(message=message)

    if "select with no columns" in msg and contains_udtf_select(query):
        # We try our best to detect if the SQL string contains a UDTF call and the output schema is empty.
        return PythonException(message=f"[UDTF_RETURN_SCHEMA_MISMATCH] {ex.message}")

    # known sql exception
    if ex.sql_error_code not in (100038, 100037, 100035, 100357):
        return None

    if "(22018): numeric value" in msg:
        return NumberFormatException(
            message='[CAST_INVALID_INPUT] Correct the value as per the syntax, or change its target type. Use `try_cast` to tolerate malformed input and return NULL instead. If necessary setting "spark.sql.ansi.enabled" to "false" may bypass this error.'
        )
    if "(22018): boolean value" in msg:
        return SparkRuntimeException(
            message='[CAST_INVALID_INPUT] Correct the value as per the syntax, or change its target type. Use `try_cast` to tolerate malformed input and return NULL instead. If necessary setting "spark.sql.ansi.enabled" to "false" may bypass this error.'
        )
    if "(22007): timestamp" in msg:
        return AnalysisException(
            "[DATATYPE_MISMATCH.UNEXPECTED_INPUT_TYPE] Data type mismatch"
        )

    if getattr(ex, "sql_error_code", None) == 100357:
        if re.search(init_multi_args_exception_pattern, msg):
            return PythonException(
                message=f"[UDTF_EXEC_ERROR] User defined table function encountered an error in the init method {ex.message}"
            )
        if re.search(terminate_multi_args_exception_pattern, msg):
            return PythonException(
                message=f"[UDTF_EXEC_ERROR] User defined table function encountered an error in the terminate method: {ex.message}"
            )

        if "failed to split string, provided pattern:" in msg:
            return IllegalArgumentException(
                message=f"Failed to split string using provided pattern. {ex.message}"
            )

        if "100357" in msg and "wrong tuple size for returned value" in msg:
            return PythonException(
                message=f"[UDTF_RETURN_SCHEMA_MISMATCH] The number of columns in the result does not match the specified schema. {ex.message}"
            )

        if "100357 (p0000): python interpreter error:" in msg:
            if "in eval" in msg:
                return PythonException(
                    message=f"[UDTF_EXEC_ERROR] User defined table function encountered an error in the 'eval' method: error. {ex.message}"
                )

            if "in terminate" in msg:
                return PythonException(
                    message=f"[UDTF_EXEC_ERROR] User defined table function encountered an error in the 'terminate' method: terminate error. {ex.message}"
                )

            if "object is not iterable" in msg and contains_udtf_select(query):
                return PythonException(
                    message=f"[UDTF_RETURN_NOT_ITERABLE] {ex.message}"
                )

            return PythonException(message=f"{ex.message}")

    return None


def build_grpc_error_response(ex: Exception) -> status_pb2.Status:
    include_stack_trace = (
        global_config.get("spark.sql.pyspark.jvmStacktrace.enabled")
        if hasattr(global_config, "spark.sql.pyspark.jvmStacktrace.enabled")
        else False
    )
    message: str | None = None

    if isinstance(ex, SnowparkClientException):
        # exceptions thrown from snowpark
        spark_java_classes = []
        match ex:
            case SnowparkSQLException():
                if ex.sql_error_code in ANALYSIS_EXCEPTION_SQL_ERROR_CODE:
                    # Data type mismatch, invalid window function
                    spark_java_classes.append("org.apache.spark.sql.AnalysisException")
                elif ex.sql_error_code == 100051:
                    spark_java_classes.append("java.lang.ArithmeticException")
                    ex = ArithmeticException(
                        error_class="DIVIDE_BY_ZERO",
                        message_parameters={"config": '"spark.sql.ansi.enabled"'},
                    )
                elif ex.sql_error_code in (100096, 100040):
                    # Spark seems to want the Java base class instead of org.apache.spark.sql.SparkDateTimeException
                    # which is what should really be thrown
                    spark_java_classes.append("java.time.DateTimeException")
                elif (
                    spark_ex := _get_converted_known_sql_or_custom_exception(ex)
                ) is not None:
                    ex = spark_ex
                    spark_java_classes.append(SPARK_PYTHON_TO_JAVA_EXCEPTION[type(ex)])
                elif ex.sql_error_code == 2043:
                    spark_java_classes.append("org.apache.spark.sql.AnalysisException")
                    message = f"does_not_exist: {str(ex)}"
                else:
                    if ex.sql_error_code == 100357:
                        # This is to handle cases that are not covered in _get_converted_known_sql_or_custom_exception for 100357.
                        spark_java_classes.append(
                            "org.apache.spark.SparkRuntimeException"
                        )
                    else:
                        # not all SnowparkSQLException correspond to QueryExecutionException. E.g., table or view not found is
                        # AnalysisException. We can gradually build a mapping if we want. The first naive version just maps
                        # to QueryExecutionException.
                        spark_java_classes.append(
                            "org.apache.spark.sql.execution.QueryExecutionException"
                        )
            case SnowparkClientException():
                # catch all
                pass

        metadata = {"classes": json.dumps(spark_java_classes)}
        if include_stack_trace:
            metadata["stackTrace"] = "".join(
                traceback.TracebackException.from_exception(ex).format()
            )
        error_info = error_details_pb2.ErrorInfo(
            reason=ex.__class__.__name__,
            domain="snowflake.snowpark",
            metadata=metadata,
        )
    elif isinstance(ex, PySparkException):
        # pyspark exceptions thrown in sas layer
        classes = type(ex).__mro__
        spark_java_classes = [
            SPARK_PYTHON_TO_JAVA_EXCEPTION[clazz]
            for clazz in classes
            if clazz in SPARK_PYTHON_TO_JAVA_EXCEPTION
        ]
        metadata = {"classes": json.dumps(spark_java_classes)}
        if include_stack_trace:
            metadata["stackTrace"] = "".join(
                traceback.TracebackException.from_exception(ex).format()
            )

        error_info = error_details_pb2.ErrorInfo(
            reason=ex.__class__.__name__,
            domain="org.apache.spark",
            metadata=metadata,
        )
    elif isinstance(ex, NotFoundError) or (
        isinstance(ex, ProgrammingError) and ex.errno == 2043
    ):
        if isinstance(ex, ProgrammingError) and ex.errno == 2043:
            message = f"does_not_exist: {str(ex)}"
        metadata = {"classes": '["org.apache.spark.sql.AnalysisException"]'}
        if include_stack_trace:
            metadata["stackTrace"] = "".join(
                traceback.TracebackException.from_exception(ex).format()
            )
        error_info = error_details_pb2.ErrorInfo(
            reason=ex.__class__.__name__,
            domain="org.apache.spark",
            metadata=metadata,
        )
    elif isinstance(ex, jpype.JException):
        java_class = ex.getClass().getName()
        metadata = {"classes": json.dumps([java_class])}
        error_info = error_details_pb2.ErrorInfo(
            reason=java_class,
            domain="org.apache.spark",
            metadata=metadata,
        )
    else:
        # unexpected exception types
        error_info = error_details_pb2.ErrorInfo(
            reason=ex.__class__.__name__,
            domain="snowflake.sas",
        )

    detail = any_pb2.Any()
    detail.Pack(error_info)

    if message is None:
        message = str(ex)

    rich_status = status_pb2.Status(
        code=code_pb2.INTERNAL, message=message, details=[detail]
    )
    return rich_status


class SparkException:
    """
    This class is used to mock exceptions created by PySpark / Spark backend in SAS layer.
    """

    @staticmethod
    def unpivot_requires_value_columns():
        return AnalysisException(
            error_class="UNPIVOT_REQUIRES_VALUE_COLUMNS", message_parameters={}
        )

    @staticmethod
    def unpivot_value_data_type_mismatch(types: str):
        return AnalysisException(
            error_class="UNPIVOT_VALUE_DATA_TYPE_MISMATCH",
            message_parameters={"types": types},
        )

    @staticmethod
    def implicit_cartesian_product(join_type: str):
        return AnalysisException(
            error_class="_LEGACY_ERROR_TEMP_1211",
            message_parameters={"joinType": join_type, "leftPlan": "leftPlan"},
        )

    @staticmethod
    def invalid_ranking_function_window_frame(
        window_frame: str,
        required: str = "specifiedwindowframe(RowFrame, unboundedpreceding$(), currentrow$()",
    ):
        return AnalysisException(
            error_class="_LEGACY_ERROR_TEMP_1036",
            message_parameters={"wf": window_frame, "required": required},
        )

    @staticmethod
    def snowpark_ddl_parser_exception(ddl: str):
        return ParseException(
            error_class="UNSUPPORTED_DATA_TYPE", message_parameters={"data_type": ddl}
        )
