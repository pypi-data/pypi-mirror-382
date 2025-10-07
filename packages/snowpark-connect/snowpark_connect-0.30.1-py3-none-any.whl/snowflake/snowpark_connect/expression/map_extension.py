#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto

import snowflake.snowpark.functions as snowpark_fn
import snowflake.snowpark_connect.proto.snowflake_expression_ext_pb2 as snowflake_proto
from snowflake.snowpark.types import (
    BooleanType,
    DayTimeIntervalType,
    StringType,
    YearMonthIntervalType,
)
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    push_evaluating_sql_scope,
    push_outer_dataframe,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

# Formatting constants for interval display
_TWO_DIGIT_FORMAT = (
    "{:02d}"  # Zero-padded 2-digit format for hours, minutes, and whole seconds
)
_THREE_DIGIT_FORMAT = (
    "{:03d}"  # Zero-padded 3-digit format for hours/minutes and whole seconds
)
_SECONDS_PRECISION_FORMAT = (
    "{:09.6f}"  # 6 decimal places with leading zeros for seconds
)


def _format_time_component(value: int, is_negative: bool = False) -> str:
    """Format a time component (hours, minutes, whole seconds) with proper zero-padding."""
    if is_negative:
        return _THREE_DIGIT_FORMAT.format(value)
    else:
        return _TWO_DIGIT_FORMAT.format(value)


def _format_seconds_precise(seconds: float) -> str:
    """Format seconds with full precision, stripping trailing zeros."""
    return _SECONDS_PRECISION_FORMAT.format(seconds).rstrip("0").rstrip(".")


def map_extension(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[list[str], TypedColumn]:
    """
    The Extension relation type contains any extensions we use for adding new
    functionality to Spark Connect.

    The extension will require new protobuf messages to be defined in the
    snowflake_connect_server/proto directory.
    """
    extension = snowflake_proto.ExpExtension()
    exp.extension.Unpack(extension)
    match extension.WhichOneof("op"):
        case "named_argument":
            from snowflake.snowpark_connect.expression.map_expression import (
                map_expression,
            )

            named_argument = extension.named_argument
            key = named_argument.key
            value = named_argument.value

            exp_name, typed_col = map_expression(value, column_mapping, typer)
            if value.HasField("literal"):
                name = key
            elif value.HasField("unresolved_attribute"):
                name = "__" + key + "__" + exp_name[0]
            else:
                raise SnowparkConnectNotImplementedError(
                    "Named argument not supported yet for this input."
                )
            return [name], typed_col

        case "interval_literal":
            interval_ext = extension.interval_literal
            literal = interval_ext.literal
            start_field = (
                interval_ext.start_field
                if interval_ext.HasField("start_field")
                else None
            )
            end_field = (
                interval_ext.end_field if interval_ext.HasField("end_field") else None
            )

            # Format interval with proper context-aware formatting
            if literal.HasField("year_month_interval"):
                total_months = literal.year_month_interval
                lit_value, lit_name = _format_year_month_interval(
                    total_months, start_field, end_field
                )
                if start_field is not None and end_field is not None:
                    interval_data_type = YearMonthIntervalType(start_field, end_field)
                else:
                    interval_data_type = YearMonthIntervalType()

                # Create column using SQL expression with context-aware formatting
                col = snowpark_fn.sql_expr(lit_value)

            elif literal.HasField("day_time_interval"):
                total_microseconds = literal.day_time_interval
                lit_value, lit_name = _format_day_time_interval(
                    total_microseconds, start_field, end_field
                )
                if start_field is not None and end_field is not None:
                    interval_data_type = DayTimeIntervalType(start_field, end_field)
                else:
                    interval_data_type = DayTimeIntervalType()

                # Create column using SQL expression to get proper interval type (same as year-month)
                col = snowpark_fn.sql_expr(lit_value)

            else:
                # Fallback - shouldn't happen
                lit_value = str(literal)
                lit_name = str(literal)
                interval_data_type = StringType()
                col = snowpark_fn.lit(lit_value)

            typed_col = TypedColumn(col, lambda: [interval_data_type])

            return [lit_name], typed_col

        case "subquery_expression":
            from snowflake.snowpark_connect.dataframe_container import (
                DataFrameContainer,
            )
            from snowflake.snowpark_connect.expression.map_expression import (
                map_expression,
            )
            from snowflake.snowpark_connect.relation.map_relation import map_relation

            current_outer_df = DataFrameContainer(
                dataframe=typer.df, column_map=column_mapping
            )

            with push_evaluating_sql_scope(), push_outer_dataframe(current_outer_df):
                df_container = map_relation(extension.subquery_expression.input)
                df = df_container.dataframe

            queries = df.queries["queries"]
            if len(queries) != 1:
                raise SnowparkConnectNotImplementedError(
                    f"Unexpected number of queries: {len(queries)}"
                )
            query = f"({queries[0]})"

            match extension.subquery_expression.subquery_type:
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_SCALAR:
                    name = "scalarsubquery()"
                    result_exp = snowpark_fn.expr(query)
                    result_type = df.schema[0].datatype
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_EXISTS:
                    name = "exists()"
                    result_exp = snowpark_fn.expr(f"(EXISTS {query})")
                    result_type = BooleanType()
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_TABLE_ARG:
                    # TODO: Currently, map_sql.py handles this, so we never end up here.
                    raise SnowparkConnectNotImplementedError("Unexpected table arg")
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_IN:
                    cols = [
                        map_expression(e, column_mapping, typer)
                        for e in extension.subquery_expression.in_subquery_values
                    ]
                    col_names_str = ", ".join(
                        col_name for col_names, _ in cols for col_name in col_names
                    )
                    # TODO: Figure out how to make a named_struct(...) here to match Spark.
                    name = f"({col_names_str}) in (listquery())"
                    result_exp = snowpark_fn.in_(
                        [col.col for _, col in cols], snowpark_fn.expr(query)
                    )
                    result_type = BooleanType()
                case other:
                    raise SnowparkConnectNotImplementedError(
                        f"Unexpected subquery type: {other}"
                    )

            return [name], TypedColumn(result_exp, lambda: [result_type])

        case other:
            raise SnowparkConnectNotImplementedError(f"Unexpected extension {other}")


def _format_year_month_interval(
    total_months: int, start_field: int | None, end_field: int | None
) -> tuple[str, str]:
    """Format year-month interval with context-aware precision."""

    # Calculate years and months from absolute value
    is_negative = total_months < 0
    abs_months = abs(total_months)
    years = abs_months // 12
    months = abs_months % 12

    # Determine interval type
    is_year_only = (
        start_field == YearMonthIntervalType.YEAR
        and end_field == YearMonthIntervalType.YEAR
    )
    is_month_only = (
        start_field == YearMonthIntervalType.MONTH
        and end_field == YearMonthIntervalType.MONTH
    )

    # Format based on type and sign
    if is_year_only:
        sign = "-" if is_negative else ""
        str_value = f"INTERVAL '{sign}{years}' YEAR"
    elif is_month_only:
        str_value = f"INTERVAL '{total_months}' MONTH"  # Keep original sign
    else:  # YEAR TO MONTH (default)
        if is_negative:
            str_value = f"INTERVAL '-{years}-{months}' YEAR TO MONTH"
        else:
            str_value = f"INTERVAL '{years}-{months}' YEAR TO MONTH"

    return str_value, str_value


def _format_day_time_interval(
    total_microseconds: int, start_field: int | None, end_field: int | None
) -> tuple[str, str]:
    """Format day-time interval with context-aware precision."""
    total_seconds = total_microseconds / 1_000_000

    # Handle negative intervals correctly
    is_negative = total_seconds < 0

    # Work with integer microseconds to preserve precision
    abs_total_microseconds = abs(total_microseconds)

    # Convert to components using integer arithmetic
    days = int(abs_total_microseconds // (86400 * 1_000_000))
    remaining_microseconds = abs_total_microseconds % (86400 * 1_000_000)
    hours = int(remaining_microseconds // (3600 * 1_000_000))
    remaining_microseconds = remaining_microseconds % (3600 * 1_000_000)
    minutes = int(remaining_microseconds // (60 * 1_000_000))
    remaining_microseconds = remaining_microseconds % (60 * 1_000_000)

    # Convert final microseconds to seconds with full precision
    seconds = remaining_microseconds / 1_000_000

    # Apply negative sign back to days if needed
    if is_negative:
        days = -days

    # Format based on the specific start/end field context
    if (
        start_field == DayTimeIntervalType.DAY and end_field == DayTimeIntervalType.DAY
    ):  # DAY only
        str_value = f"INTERVAL '{days}' DAY"
    elif (
        start_field == DayTimeIntervalType.HOUR
        and end_field == DayTimeIntervalType.HOUR
    ):  # HOUR only
        # For HOUR-only intervals, calculate total hours (don't break down into days)
        total_hours = int(abs(total_microseconds) // (3600 * 1_000_000))
        if total_microseconds < 0:
            total_hours = -total_hours
        if total_hours >= 0:
            str_value = f"INTERVAL '{_TWO_DIGIT_FORMAT.format(total_hours)}' HOUR"
        else:
            str_value = f"INTERVAL '{_THREE_DIGIT_FORMAT.format(total_hours)}' HOUR"
    elif (
        start_field == DayTimeIntervalType.MINUTE
        and end_field == DayTimeIntervalType.MINUTE
    ):  # MINUTE only
        # For MINUTE-only intervals, calculate total minutes (don't break down into hours/days)
        total_minutes = int(abs(total_microseconds) // (60 * 1_000_000))
        if total_microseconds < 0:
            total_minutes = -total_minutes
        if total_minutes >= 0:
            str_value = f"INTERVAL '{_TWO_DIGIT_FORMAT.format(total_minutes)}' MINUTE"
        else:
            str_value = f"INTERVAL '{_THREE_DIGIT_FORMAT.format(total_minutes)}' MINUTE"
    elif (
        start_field == DayTimeIntervalType.SECOND
        and end_field == DayTimeIntervalType.SECOND
    ):  # SECOND only
        # For SECOND-only intervals, use total seconds (don't break down into minutes/hours/days)
        total_seconds_precise = total_microseconds / 1_000_000
        if total_seconds_precise == int(total_seconds_precise):
            if total_seconds_precise >= 0:
                str_value = f"INTERVAL '{_TWO_DIGIT_FORMAT.format(int(total_seconds_precise))}' SECOND"
            else:
                str_value = f"INTERVAL '{_THREE_DIGIT_FORMAT.format(int(total_seconds_precise))}' SECOND"
        else:
            seconds_str = _format_seconds_precise(total_seconds_precise)
            str_value = f"INTERVAL '{seconds_str}' SECOND"
    elif (
        start_field == DayTimeIntervalType.MINUTE
        and end_field == DayTimeIntervalType.SECOND
    ):  # MINUTE TO SECOND
        # For MINUTE TO SECOND intervals, calculate total minutes and remaining seconds
        total_minutes = int(abs_total_microseconds // (60 * 1_000_000))
        remaining_microseconds_for_minutes = abs_total_microseconds % (60 * 1_000_000)
        remaining_seconds_for_minutes = remaining_microseconds_for_minutes / 1_000_000

        # Format seconds appropriately (whole or fractional)
        if remaining_seconds_for_minutes == int(remaining_seconds_for_minutes):
            seconds_str = _TWO_DIGIT_FORMAT.format(int(remaining_seconds_for_minutes))
        else:
            seconds_str = _format_seconds_precise(remaining_seconds_for_minutes)

        # Apply sign and format
        if is_negative:
            str_value = f"INTERVAL '-{_TWO_DIGIT_FORMAT.format(total_minutes)}:{seconds_str}' MINUTE TO SECOND"
        else:
            str_value = f"INTERVAL '{_TWO_DIGIT_FORMAT.format(total_minutes)}:{seconds_str}' MINUTE TO SECOND"
    elif (
        start_field == DayTimeIntervalType.HOUR
        and end_field == DayTimeIntervalType.MINUTE
    ):  # HOUR TO MINUTE
        str_value = f"INTERVAL '{_TWO_DIGIT_FORMAT.format(hours)}:{_TWO_DIGIT_FORMAT.format(minutes)}' HOUR TO MINUTE"
    elif (
        start_field == DayTimeIntervalType.HOUR
        and end_field == DayTimeIntervalType.SECOND
    ):  # HOUR TO SECOND
        if seconds == int(seconds):
            str_value = f"INTERVAL '{_format_time_component(hours)}:{_format_time_component(minutes)}:{_format_time_component(int(seconds))}' HOUR TO SECOND"
        else:
            seconds_str = _format_seconds_precise(seconds)
            str_value = f"INTERVAL '{_format_time_component(hours)}:{_format_time_component(minutes)}:{seconds_str}' HOUR TO SECOND"
    elif (
        start_field == DayTimeIntervalType.DAY and end_field == DayTimeIntervalType.HOUR
    ):  # DAY TO HOUR
        str_value = f"INTERVAL '{days} {_format_time_component(hours)}' DAY TO HOUR"
    elif (
        start_field == DayTimeIntervalType.DAY
        and end_field == DayTimeIntervalType.MINUTE
    ):  # DAY TO MINUTE
        str_value = f"INTERVAL '{days} {_format_time_component(hours)}:{_format_time_component(minutes)}' DAY TO MINUTE"
    elif (
        start_field == DayTimeIntervalType.DAY
        and end_field == DayTimeIntervalType.SECOND
    ):  # DAY TO SECOND
        if seconds == int(seconds):
            str_value = f"INTERVAL '{days} {_format_time_component(hours)}:{_format_time_component(minutes)}:{_format_time_component(int(seconds))}' DAY TO SECOND"
        else:
            seconds_str = _format_seconds_precise(seconds)
            str_value = f"INTERVAL '{days} {_format_time_component(hours)}:{_format_time_component(minutes)}:{seconds_str}' DAY TO SECOND"
    else:
        # Fallback - use smart formatting like the original literal.py logic
        if days > 0:
            if hours == 0 and minutes == 0 and seconds == 0:
                str_value = f"INTERVAL '{int(days)}' DAY"
            else:
                if seconds == int(seconds):
                    str_value = f"INTERVAL '{days} {_format_time_component(hours)}:{_format_time_component(minutes)}:{_format_time_component(int(seconds))}' DAY TO SECOND"
                else:
                    seconds_str = _format_seconds_precise(seconds)
                    str_value = f"INTERVAL '{days} {_format_time_component(hours)}:{_format_time_component(minutes)}:{seconds_str}' DAY TO SECOND"
        elif hours > 0:
            if minutes == 0 and seconds == 0:
                str_value = f"INTERVAL '{_format_time_component(hours)}' HOUR"
            else:
                if seconds == int(seconds):
                    str_value = f"INTERVAL '{_format_time_component(hours)}:{_format_time_component(minutes)}:{_format_time_component(int(seconds))}' HOUR TO SECOND"
                else:
                    seconds_str = _format_seconds_precise(seconds)
                    str_value = f"INTERVAL '{_format_time_component(hours)}:{_format_time_component(minutes)}:{seconds_str}' HOUR TO SECOND"
        elif minutes > 0:
            if seconds == 0:
                str_value = f"INTERVAL '{_format_time_component(minutes)}' MINUTE"
            else:
                if seconds == int(seconds):
                    str_value = f"INTERVAL '{_format_time_component(minutes)}:{_format_time_component(int(seconds))}' MINUTE TO SECOND"
                else:
                    seconds_str = _format_seconds_precise(seconds)
                    str_value = f"INTERVAL '{_format_time_component(minutes)}:{seconds_str}' MINUTE TO SECOND"
        else:
            if seconds == int(seconds):
                str_value = f"INTERVAL '{_format_time_component(int(seconds))}' SECOND"
            else:
                seconds_str = _format_seconds_precise(seconds)
                str_value = f"INTERVAL '{seconds_str}' SECOND"

    return str_value, str_value
