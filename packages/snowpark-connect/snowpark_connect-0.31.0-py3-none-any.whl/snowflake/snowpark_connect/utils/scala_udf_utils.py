#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
"""
Scala UDF utilities for Snowpark Connect.

This module provides utilities for creating and managing Scala User-Defined Functions (UDFs)
in Snowflake through Snowpark Connect. It handles the conversion between different type systems
(Snowpark, Scala, Snowflake, Spark protobuf) and generates the necessary SQL DDL statements
for UDF creation.

Key components:
- ScalaUdf: Reference class for Scala UDFs
- ScalaUDFDef: Definition class for Scala UDF creation
- Type mapping functions for different type systems
- UDF creation and management utilities
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Union

import snowflake.snowpark.types as snowpark_type
import snowflake.snowpark_connect.includes.python.pyspark.sql.connect.proto.types_pb2 as types_proto
from snowflake.snowpark_connect.error.error_codes import ErrorCodes
from snowflake.snowpark_connect.error.error_utils import attach_custom_error_code
from snowflake.snowpark_connect.resources_initializer import RESOURCE_PATH
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.udf_utils import (
    ProcessCommonInlineUserDefinedFunction,
)

# Prefix used for internally generated Scala UDF names to avoid conflicts
CREATE_SCALA_UDF_PREFIX = "__SC_BUILD_IN_CREATE_UDF_SCALA_"


class ScalaUdf:
    """
    Reference class for Scala UDFs, providing similar properties like Python UserDefinedFunction.

    This class serves as a lightweight reference to a Scala UDF that has been created
    in Snowflake, storing the essential metadata needed for function calls.
    """

    def __init__(
        self,
        name: str,
        input_types: List[snowpark_type.DataType],
        return_type: snowpark_type.DataType,
    ) -> None:
        """
        Initialize a Scala UDF reference.

        Args:
            name: The name of the UDF in Snowflake
            input_types: List of input parameter types
            return_type: The return type of the UDF
        """
        self.name = name
        self._input_types = input_types
        self._return_type = return_type


@dataclass(frozen=True)
class Param:
    """
    Represents a function parameter with name and data type.

    Attributes:
        name: Parameter name
        data_type: Parameter data type as a string
    """

    name: str
    data_type: str


@dataclass(frozen=True)
class NullHandling(str, Enum):
    """
    Enumeration for UDF null handling behavior.

    Determines how the UDF behaves when input parameters contain null values.
    """

    RETURNS_NULL_ON_NULL_INPUT = "RETURNS NULL ON NULL INPUT"
    CALLED_ON_NULL_INPUT = "CALLED ON NULL INPUT"


@dataclass(frozen=True)
class ReturnType:
    """
    Represents the return type of a function.

    Attributes:
        data_type: Return data type as a string
    """

    data_type: str


@dataclass(frozen=True)
class Signature:
    """
    Represents a function signature with parameters and return type.

    Attributes:
        params: List of function parameters
        returns: Function return type
    """

    params: List[Param]
    returns: ReturnType


@dataclass(frozen=True)
class ScalaUDFDef:
    """
    Complete definition for creating a Scala UDF in Snowflake.

    Contains all the information needed to generate the CREATE FUNCTION SQL statement
    and the Scala code body for the UDF.

    Attributes:
        name: UDF name
        signature: SQL signature (for Snowflake function definition)
        scala_signature: Scala signature (for Scala code generation)
        imports: List of JAR files to import
        null_handling: Null handling behavior (defaults to RETURNS_NULL_ON_NULL_INPUT)
    """

    name: str
    signature: Signature
    scala_signature: Signature
    scala_invocation_args: List[str]
    imports: List[str]
    null_handling: NullHandling = NullHandling.RETURNS_NULL_ON_NULL_INPUT

    # -------------------- DDL Emitter --------------------

    def _gen_body_scala(self) -> str:
        """
        Generate the Scala code body for the UDF.

        Creates a Scala object that loads the serialized function from a binary file
        and provides a run method to execute it.

        Returns:
            String containing the complete Scala code for the UDF body
        """
        # Convert Array to Seq for Scala compatibility in function signatures.
        udf_func_input_types = (
            ", ".join(p.data_type for p in self.scala_signature.params)
        ).replace("Array", "Seq")
        # Create the Scala arguments and input types string: "arg0: Type0, arg1: Type1, ...".
        joined_wrapper_arg_and_input_types_str = ", ".join(
            f"{p.name}: {p.data_type}" for p in self.scala_signature.params
        )
        # This is used in defining the input types for the wrapper function. For Maps to work correctly with Scala UDFs,
        # we need to set the Map types to Map[String, String]. These get cast to the respective original types
        # when the original UDF function is invoked.
        wrapper_arg_and_input_types_str = re.sub(
            pattern=r"Map\[\w+,\s\w+\]",
            repl="Map[String, String]",
            string=joined_wrapper_arg_and_input_types_str,
        )
        invocation_args = ", ".join(self.scala_invocation_args)

        # Cannot directly return a map from a Scala UDF due to issues with non-String values. Snowflake SQL Scala only
        # supports Map[String, String] as input types. Therefore, we convert the map to a JSON string before returning.
        # This is processed as a Variant by SQL.
        udf_func_return_type = self.scala_signature.returns.data_type
        is_map_return = udf_func_return_type.startswith("Map")
        wrapper_return_type = "String" if is_map_return else udf_func_return_type

        # For handling Seq type correctly, ensure that the wrapper function always uses Array as its input and
        # return types (when required) and the wrapped function uses Seq.
        udf_func_return_type = udf_func_return_type.replace("Array", "Seq")
        is_seq_return = udf_func_return_type.startswith("Seq")

        # Need to call the map to JSON string converter when a map is returned by the user's function.
        if is_map_return:
            invoke_udf_func = f"write(func({invocation_args}))"
        elif is_seq_return:
            # TODO: SNOW-2339385 Handle Array[T] return types correctly. Currently, only Seq[T] is supported.
            invoke_udf_func = f"func({invocation_args}).toArray"
        else:
            invoke_udf_func = f"func({invocation_args})"

        # The lines of code below are required only when a Map is returned by the UDF. This is needed to serialize the
        # map output to a JSON string.
        map_return_imports = (
            ""
            if not is_map_return
            else """
import shaded_json4s._
import shaded_json4s.native.Serialization._
import shaded_json4s.native.Serialization
"""
        )
        map_return_formatter = (
            ""
            if not is_map_return
            else """
  implicit val formats = Serialization.formats(NoTypeHints)
"""
        )

        return f"""import org.apache.spark.sql.connect.common.UdfPacket
{map_return_imports}
import com.snowflake.sas.scala.Utils

object __RecreatedSparkUdf {{
  {map_return_formatter}
  private lazy val func: ({udf_func_input_types}) => {udf_func_return_type} =
    Utils.deserializeFunc("{self.name}.bin").asInstanceOf[({udf_func_input_types}) => {udf_func_return_type}]

  def __wrapperFunc({wrapper_arg_and_input_types_str}): {wrapper_return_type} = {{
    {invoke_udf_func}
  }}
}}
"""

    def to_create_function_sql(self) -> str:
        """
        Generate the complete CREATE FUNCTION SQL statement for the Scala UDF.

        Creates a Snowflake CREATE OR REPLACE TEMPORARY FUNCTION statement with
        all necessary clauses including language, runtime version, packages,
        imports, and the Scala code body.

        Returns:
            Complete SQL DDL statement for creating the UDF
        """
        # self.validate()

        args = ", ".join(f"{p.name} {p.data_type}" for p in self.signature.params)
        ret_type = self.signature.returns.data_type

        def quote_single(s: str) -> str:
            """Helper function to wrap strings in single quotes for SQL."""
            return "'" + s + "'"

        # Handler and imports
        imports_sql = f"IMPORTS = ({', '.join(quote_single(x) for x in self.imports)})"

        return f"""
CREATE OR REPLACE TEMPORARY FUNCTION {self.name}({args})
RETURNS {ret_type}
LANGUAGE SCALA
{self.null_handling.value}
RUNTIME_VERSION = 2.12
PACKAGES = ('com.snowflake:snowpark:latest')
{imports_sql}
HANDLER = '__RecreatedSparkUdf.__wrapperFunc'
AS
$$
{self._gen_body_scala()}
$$;"""


def build_scala_udf_imports(session, payload, udf_name, is_map_return) -> List[str]:
    """
    Build the list of imports needed for the Scala UDF.

    This function:
    1. Saves the UDF payload to a binary file in the session stage
    2. Collects user-uploaded JAR files from the stage
    3. Returns a list of all required JAR files for the UDF

    Args:
        session: Snowpark session
        payload: Binary payload containing the serialized UDF
        udf_name: Name of the UDF (used for the binary file name)
        is_map_return: Indicates if the UDF returns a Map (affects imports)

    Returns:
        List of JAR file paths to be imported by the UDF
    """
    # Save pciudf._payload to a bin file:
    import io

    payload_as_stream = io.BytesIO(payload)
    stage = session.get_session_stage()
    stage_resource_path = stage + RESOURCE_PATH
    closure_binary_file = stage_resource_path + "/" + udf_name + ".bin"
    session.file.put_stream(
        payload_as_stream,
        closure_binary_file,
        overwrite=True,
    )

    # Get a list of the jar files uploaded to the stage. We need to import the user's jar for the Scala UDF.
    res = session.sql(rf"LIST {stage}/ PATTERN='.*\.jar';").collect()
    user_jars = []
    for row in res:
        if RESOURCE_PATH not in row[0]:
            # Remove the stage path since it is not properly formatted.
            user_jars.append(row[0][row[0].find("/") :])

    # Format the user jars to be used in the IMPORTS clause of the stored procedure.
    return [
        closure_binary_file,
        f"{stage_resource_path}/spark-connect-client-jvm_2.12-3.5.6.jar",
        f"{stage_resource_path}/spark-common-utils_2.12-3.5.6.jar",
        f"{stage_resource_path}/spark-sql_2.12-3.5.6.jar",
        f"{stage_resource_path}/json4s-ast_2.12-3.7.0-M11.jar",
        f"{stage_resource_path}/sas-scala-udf_2.12-0.1.0.jar",
    ] + [f"{stage + jar}" for jar in user_jars]


def create_scala_udf(pciudf: ProcessCommonInlineUserDefinedFunction) -> ScalaUdf:
    """
    Create a Scala UDF in Snowflake from a ProcessCommonInlineUserDefinedFunction object.

    This function handles the complete process of creating a Scala UDF:
    1. Generates a unique function name if not provided
    2. Checks for existing UDFs in the session cache
    3. Creates the necessary imports list
    4. Maps types between different systems (Snowpark, Scala, Snowflake)
    5. Generates and executes the CREATE FUNCTION SQL statement

    If the UDF already exists in the session cache, it will be reused.

    Args:
        pciudf: The ProcessCommonInlineUserDefinedFunction object containing UDF details.

    Returns:
        A ScalaUdf object representing the created or cached Scala UDF.
    """
    from snowflake.snowpark_connect.resources_initializer import (
        wait_for_resource_initialization,
    )

    # Make sure that the resource initializer thread is completed before creating Scala UDFs since we depend on the jars
    # uploaded by it.
    wait_for_resource_initialization()

    from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session

    function_name = pciudf._function_name
    # If a function name is not provided, hash the binary file and use the first ten characters as the function name.
    if not function_name:
        import hashlib

        function_name = hashlib.sha256(pciudf._payload).hexdigest()[:10]
    udf_name = CREATE_SCALA_UDF_PREFIX + function_name

    session = get_or_create_snowpark_session()
    if udf_name in session._udfs:
        cached_udf = session._udfs[udf_name]
        return ScalaUdf(cached_udf.name, cached_udf.input_types, cached_udf.return_type)

    # In case the Scala UDF was created with `spark.udf.register`, the Spark Scala input types (from protobuf) are
    # stored in pciudf.scala_input_types.
    # We cannot rely solely on the inputTypes field from the Scala UDF or the Snowpark input types, since:
    # - spark.udf.register arguments come from the inputTypes field
    # - UDFs created with a data type (like below) do not populate the inputTypes field. This requires the input types
    #   inferred by Snowpark. e.g.: udf((i: Long) => (i + 1).toInt, IntegerType)
    input_types = (
        pciudf._scala_input_types if pciudf._scala_input_types else pciudf._input_types
    )

    scala_input_params: List[Param] = []
    sql_input_params: List[Param] = []
    scala_invocation_args: List[str] = []  # arguments passed into the udf function
    if input_types:  # input_types can be None when no arguments are provided
        for i, input_type in enumerate(input_types):
            param_name = "arg" + str(i)
            # Create the Scala arguments and input types string: "arg0: Type0, arg1: Type1, ...".
            scala_input_params.append(
                Param(param_name, map_type_to_scala_type(input_type))
            )
            # Create the Snowflake SQL arguments and input types string: "arg0 TYPE0, arg1 TYPE1, ...".
            sql_input_params.append(
                Param(param_name, map_type_to_snowflake_type(input_type))
            )
            # In the case of Map input types, we need to cast the argument to the correct type in Scala.
            # Snowflake SQL Scala can only handle MAP[VARCHAR, VARCHAR] as input types.
            scala_invocation_args.append(
                cast_scala_map_args_from_given_type(param_name, input_type)
            )

    scala_return_type = map_type_to_scala_type(pciudf._original_return_type)
    # If the SQL return type is a MAP, change this to VARIANT because of issues with Scala UDFs.
    sql_return_type = map_type_to_snowflake_type(pciudf._original_return_type)
    imports = build_scala_udf_imports(
        session,
        pciudf._payload,
        udf_name,
        is_map_return=sql_return_type.startswith("MAP"),
    )
    sql_return_type = (
        "VARIANT" if sql_return_type.startswith("MAP") else sql_return_type
    )

    udf_def = ScalaUDFDef(
        name=udf_name,
        signature=Signature(
            params=sql_input_params, returns=ReturnType(sql_return_type)
        ),
        imports=imports,
        scala_signature=Signature(
            params=scala_input_params, returns=ReturnType(scala_return_type)
        ),
        scala_invocation_args=scala_invocation_args,
    )
    create_udf_sql = udf_def.to_create_function_sql()
    logger.info(f"Creating Scala UDF: {create_udf_sql}")
    session.sql(create_udf_sql).collect()
    return ScalaUdf(udf_name, pciudf._input_types, pciudf._return_type)


def map_type_to_scala_type(
    t: Union[snowpark_type.DataType, types_proto.DataType]
) -> str:
    """Maps a Snowpark or Spark protobuf type to a Scala type string."""
    if not t:
        return "String"
    is_snowpark_type = isinstance(t, snowpark_type.DataType)
    condition = type(t) if is_snowpark_type else t.WhichOneof("kind")
    match condition:
        case snowpark_type.ArrayType | "array":
            return (
                f"Array[{map_type_to_scala_type(t.element_type)}]"
                if is_snowpark_type
                else f"Array[{map_type_to_scala_type(t.array.element_type)}]"
            )
        case snowpark_type.BinaryType | "binary":
            return "Array[Byte]"
        case snowpark_type.BooleanType | "boolean":
            return "Boolean"
        case snowpark_type.ByteType | "byte":
            return "Byte"
        case snowpark_type.DateType | "date":
            return "java.sql.Date"
        case snowpark_type.DecimalType | "decimal":
            return "java.math.BigDecimal"
        case snowpark_type.DoubleType | "double":
            return "Double"
        case snowpark_type.FloatType | "float":
            return "Float"
        case snowpark_type.GeographyType:
            return "Geography"
        case snowpark_type.IntegerType | "integer":
            return "Int"
        case snowpark_type.LongType | "long":
            return "Long"
        case snowpark_type.MapType | "map":  # can also map to OBJECT in Snowflake
            key_type = (
                map_type_to_scala_type(t.key_type)
                if is_snowpark_type
                else map_type_to_scala_type(t.map.key_type)
            )
            value_type = (
                map_type_to_scala_type(t.value_type)
                if is_snowpark_type
                else map_type_to_scala_type(t.map.value_type)
            )
            return f"Map[{key_type}, {value_type}]"
        case snowpark_type.NullType | "null":
            return "String"  # cannot set the return type to Null in Snowpark Scala UDFs
        case snowpark_type.ShortType | "short":
            return "Short"
        case snowpark_type.StringType | "string" | "char" | "varchar":
            return "String"
        case snowpark_type.TimestampType | "timestamp" | "timestamp_ntz":
            return "java.sql.Timestamp"
        case snowpark_type.VariantType:
            return "Variant"
        case _:
            exception = ValueError(f"Unsupported Snowpark type: {t}")
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
            raise exception


def map_type_to_snowflake_type(
    t: Union[snowpark_type.DataType, types_proto.DataType]
) -> str:
    """Maps a Snowpark or Spark protobuf type to a Snowflake type string."""
    if not t:
        return "VARCHAR"
    is_snowpark_type = isinstance(t, snowpark_type.DataType)
    condition = type(t) if is_snowpark_type else t.WhichOneof("kind")
    match condition:
        case snowpark_type.ArrayType | "array":
            return (
                f"ARRAY({map_type_to_snowflake_type(t.element_type)})"
                if is_snowpark_type
                else f"ARRAY({map_type_to_snowflake_type(t.array.element_type)})"
            )
        case snowpark_type.BinaryType | "binary":
            return "BINARY"
        case snowpark_type.BooleanType | "boolean":
            return "BOOLEAN"
        case snowpark_type.ByteType | "byte":
            return "TINYINT"
        case snowpark_type.DateType | "date":
            return "DATE"
        case snowpark_type.DecimalType | "decimal":
            return "NUMBER"
        case snowpark_type.DoubleType | "double":
            return "DOUBLE"
        case snowpark_type.FloatType | "float":
            return "FLOAT"
        case snowpark_type.GeographyType:
            return "GEOGRAPHY"
        case snowpark_type.IntegerType | "integer":
            return "INT"
        case snowpark_type.LongType | "long":
            return "BIGINT"
        case snowpark_type.MapType | "map":
            # Maps to OBJECT in Snowflake if key and value types are not specified.
            key_type = (
                map_type_to_snowflake_type(t.key_type)
                if is_snowpark_type
                else map_type_to_snowflake_type(t.map.key_type)
            )
            value_type = (
                map_type_to_snowflake_type(t.value_type)
                if is_snowpark_type
                else map_type_to_snowflake_type(t.map.value_type)
            )
            return (
                f"MAP({key_type}, {value_type})"
                if key_type and value_type
                else "OBJECT"
            )
        case snowpark_type.NullType | "null":
            return "VARCHAR"
        case snowpark_type.ShortType | "short":
            return "SMALLINT"
        case snowpark_type.StringType | "string" | "char" | "varchar":
            return "VARCHAR"
        case snowpark_type.TimestampType | "timestamp" | "timestamp_ntz":
            return "TIMESTAMP"
        case snowpark_type.VariantType:
            return "VARIANT"
        case _:
            exception = ValueError(f"Unsupported Snowpark type: {t}")
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
            raise exception


def cast_scala_map_args_from_given_type(
    arg_name: str, input_type: Union[snowpark_type.DataType, types_proto.DataType]
) -> str:
    """If the input_type is a Map, cast the argument arg_name to a Map[key_type, value_type] in Scala."""
    is_snowpark_type = isinstance(input_type, snowpark_type.DataType)

    def convert_from_string_to_type(
        arg_name: str, t: Union[snowpark_type.DataType, types_proto.DataType]
    ) -> str:
        """Convert the string argument arg_name to the specified type t in Scala."""
        condition = type(t) if is_snowpark_type else t.WhichOneof("kind")
        match condition:
            case snowpark_type.BinaryType | "binary":
                return arg_name + ".getBytes()"
            case snowpark_type.BooleanType | "boolean":
                return arg_name + ".toBoolean"
            case snowpark_type.ByteType | "byte":
                return arg_name + ".getBytes().head"  # TODO: verify if this is correct
            case snowpark_type.DateType | "date":
                return f"java.sql.Date.valueOf({arg_name})"
            case snowpark_type.DecimalType | "decimal":
                return f"new BigDecimal({arg_name})"
            case snowpark_type.DoubleType | "double":
                return arg_name + ".toDouble"
            case snowpark_type.FloatType | "float":
                return arg_name + ".toFloat"
            case snowpark_type.IntegerType | "integer":
                return arg_name + ".toInt"
            case snowpark_type.LongType | "long":
                return arg_name + ".toLong"
            case snowpark_type.ShortType | "short":
                return arg_name + ".toShort"
            case snowpark_type.StringType | "string" | "char" | "varchar":
                return arg_name
            case snowpark_type.TimestampType | "timestamp" | "timestamp_ntz":
                return "java.sql.Timestamp.valueOf({arg_name})"
            case _:
                exception = ValueError(f"Unsupported Snowpark type: {t}")
                attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_TYPE)
                raise exception

    if (is_snowpark_type and isinstance(input_type, snowpark_type.MapType)) or (
        not is_snowpark_type and input_type.WhichOneof("kind") == "map"
    ):
        key_type = input_type.key_type if is_snowpark_type else input_type.map.key_type
        value_type = (
            input_type.value_type if is_snowpark_type else input_type.map.value_type
        )
        return f"{arg_name}.map {{ case (k, v) => ({convert_from_string_to_type('k', key_type)}, {convert_from_string_to_type('v', value_type)})}}"
    else:
        return arg_name
