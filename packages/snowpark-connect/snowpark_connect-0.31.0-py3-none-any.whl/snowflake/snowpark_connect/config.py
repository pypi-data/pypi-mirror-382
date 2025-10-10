#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

# Proto source for reference:
# https://github.com/apache/spark/blob/branch-3.5/connector/connect/common/src/main/protobuf/spark/connect/base.proto#L420
import re
import sys
from collections import defaultdict
from copy import copy, deepcopy
from typing import Any, Dict

import jpype
import pyspark.sql.connect.proto.base_pb2 as proto_base
from tzlocal import get_localzone_name

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
    unquote_if_quoted,
)
from snowflake.snowpark.exceptions import SnowparkSQLException
from snowflake.snowpark.types import TimestampTimeZone, TimestampType
from snowflake.snowpark_connect.error.error_codes import ErrorCodes
from snowflake.snowpark_connect.error.error_utils import attach_custom_error_code
from snowflake.snowpark_connect.utils.concurrent import SynchronizedDict
from snowflake.snowpark_connect.utils.context import (
    get_jpype_jclass_lock,
    get_session_id,
)
from snowflake.snowpark_connect.utils.external_udxf_cache import (
    clear_external_udxf_cache,
)
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
    telemetry,
)
from snowflake.snowpark_connect.version import VERSION as sas_version


def str_to_bool(boolean_str: str) -> bool:
    assert boolean_str in (
        "True",
        "true",
        "False",
        "false",
        "1",
        "0",
        "",  # This is the default value, equivalent to False.
    ), f"Invalid boolean value: {boolean_str}"
    return boolean_str in ["True", "true", "1"]


class GlobalConfig:
    """This class contains the global configuration for the Spark Server."""

    default_static_global_config = {
        # Defaults from Spark https://github.com/apache/spark/blob/master/sql/catalyst/src/main/scala/org/apache/spark/sql/internal/SQLConf.scala
        "spark.sql.warehouse.dir": None,
        "spark.sql.catalogImplementation": "in-memory",
        "spark.sql.sources.schemaStringLengthThreshold": 4000,
        "spark.sql.filesourceTableRelationCacheSize": 1000,
        "spark.sql.codegen.cache.maxEntries": 100,
        "spark.sql.codegen.comments": False,
        "spark.sql.debug": False,
        "spark.sql.hive.thriftServer.singleSession": False,
        "spark.sql.extensions": None,
        "spark.sql.cache.serializer": "org.apache.spark.sql.execution.columnar.DefaultCachedBatchSerializer",
        "spark.sql.queryExecutionListeners": 1000,
        "spark.sql.shuffleExchange.maxThreadThreshold": 1024,
        "spark.sql.broadcastExchange.maxThreadThreshold": 128,
        "spark.sql.subquery.maxThreadThreshold": 16,
        "spark.sql.resultQueryStage.maxThreadThreshold": 1024,
        "spark.sql.event.truncate.length": sys.maxsize,
        "spark.sql.legacy.sessionInitWithConfigDefaults": False,
        "spark.sql.defaultUrlStreamHandlerFactory.enabled": True,
        "spark.sql.streaming.ui.enabled": True,
        "spark.sql.streaming.ui.retainedProgressUpdates": 100,
        "spark.sql.streaming.ui.retainedQueries": 100,
        "spark.sql.metadataCacheTTLSeconds": -1,
        "spark.sql.streaming.ui.enabledCustomMetricList": None,
        "spark.sql.sources.disabledJdbcConnProviderList": "",
        "spark.python.sql.dataFrameDebugging.enabled": True,
        "spark.sql.extensions.test.loadFromCp": None,
        "spark.sql.streaming.streamingQueryListeners": None,
        # Defaults from Spark https://github.com/apache/spark/blob/master/sql/connect/server/src/main/scala/org/apache/spark/sql/connect/config/Connect.scala
        "spark.connect.grpc.binding.address": 15002,
        "spark.connect.grpc.port.maxRetries": 0,
        "spark.connect.grpc.interceptor.classes": 128 * 1024 * 1024,
        "spark.connect.grpc.maxInboundMessageSize": 128 * 1024 * 1024,
        "spark.connect.grpc.marshallerRecursionLimit": 1024,
        "spark.connect.session.manager.defaultSessionTimeout": True,
        "spark.connect.execute.reattachable.senderMaxStreamDuration": None,
        "spark.connect.extensions.expression.classes": None,
        "spark.connect.extensions.command.classes": None,
        "spark.connect.jvmStacktrace.maxSize": 1024,
        "spark.sql.connect.ui.retainedStatements": 200,
        "spark.connect.copyFromLocalToFs.allowDestLocal": False,
        "spark.sql.connect.ui.retainedSessions": 200,
        "spark.connect.grpc.maxMetadataSize": 1024,
        "spark.connect.session.planCache.maxSize": 16,
        "spark.connect.authenticate.token": True,
        "spark.connect.grpc.binding.port": None,
        "spark.connect.grpc.arrow.maxBatchSize": None,
        # Defaults from Spark https://github.com/apache/spark/blob/master/sql/hive/src/main/scala/org/apache/spark/sql/hive/HiveUtils.scala
        "spark.sql.hive.version": "2.3.9",
        "spark.sql.hive.metastore.version": "2.3.9",
        "spark.sql.hive.metastore.jars": "builtin",
        "spark.sql.hive.metastore.jars.path": None,
        "spark.sql.hive.metastore.sharedPrefixes": [
            "com.mysql.jdbc",
            "com.mysql.cj",
            "org.postgresql",
            "com.microsoft.sqlserver",
            "oracle.jdbc",
        ],
        "spark.sql.hive.metastore.barrierPrefixes": None,
        "spark.sql.globalTempDatabase": "global_temp",
    }

    readonly_config_list = [
        "snowpark.connect.version",
    ]

    default_global_config = {
        # TODO: This will need to be changed to the actual host of the driver.
        "spark.driver.host": "sc://localhost:15002",
        "spark.sql.pyspark.inferNestedDictAsStruct.enabled": "false",
        "spark.sql.pyspark.legacy.inferArrayTypeFromFirstElement.enabled": "false",
        "spark.sql.repl.eagerEval.enabled": "false",
        "spark.sql.repl.eagerEval.maxNumRows": "20",
        "spark.sql.repl.eagerEval.truncate": "20",
        "spark.sql.session.localRelationCacheThreshold": "2147483647",
        "spark.sql.session.timeZone": get_localzone_name(),  # spark by default uses jvm local timezone
        "spark.sql.timestampType": "TIMESTAMP_LTZ",
        "spark.sql.crossJoin.enabled": "true",
        "spark.sql.caseSensitive": "false",
        "spark.sql.mapKeyDedupPolicy": "EXCEPTION",
        "spark.sql.ansi.enabled": "false",
        "spark.sql.legacy.allowHashOnMapType": "false",
        "spark.sql.sources.default": "parquet",
        "spark.Catalog.databaseFilterInformationSchema": "false",
        "spark.sql.parser.quotedRegexColumnNames": "false",
        # custom configs
        "snowpark.connect.version": ".".join(map(str, sas_version)),
        # Control whether repartition(n) on a DataFrame forces splitting into n files during writes
        # This matches spark behavior more closely, but introduces overhead.
        "snowflake.repartition.for.writes": "false",
        "snowpark.connect.structured_types.fix": str(
            snowpark.context._enable_fix_2360274
        ).lower(),
    }

    boolean_config_list = [
        "spark.sql.pyspark.inferNestedDictAsStruct.enabled",
        "spark.sql.pyspark.legacy.inferArrayTypeFromFirstElement.enabled",
        "spark.sql.repl.eagerEval.enabled",
        "spark.sql.crossJoin.enabled",
        "spark.sql.caseSensitive",
        "spark.sql.ansi.enabled",
        "spark.sql.legacy.allowHashOnMapType",
        "spark.Catalog.databaseFilterInformationSchema",
        "spark.sql.parser.quotedRegexColumnNames",
        "snowflake.repartition.for.writes",
    ]

    int_config_list = [
        "spark.sql.repl.eagerEval.maxNumRows",
        "spark.sql.repl.eagerEval.truncate",
        "spark.sql.session.localRelationCacheThreshold",
    ]

    # This is a mapping of the configuration key to a function that assigns the
    # configuration value to a Snowpark session. This is only needed for configurations
    # that we need to make available to the Snowpark session.
    snowpark_config_mapping = {
        # Snowpark uses query_tag for the application name.
        "spark.app.name": lambda session, name: setattr(
            session, "query_tag", f"Spark-Connect-App-Name={name}"
        ),
        "snowpark.connect.udf.imports": lambda session, imports: parse_imports(
            session, imports
        ),
    }

    float_config_list = []

    def __init__(self) -> None:
        self.global_config = SynchronizedDict(copy(self.default_global_config))
        for key in self.global_config.keys():
            setattr(self, key.replace(".", "_"), self._get_config_setting(key))

    def _get_config_setting(self, key: str) -> bool | int | float | str | None:
        """Get the configuration setting for the key based on the setting type."""
        if key in self.boolean_config_list:
            return str_to_bool(self.global_config[key])
        elif key in self.int_config_list:
            return int(self.global_config[key])
        elif key in self.float_config_list:
            return float(self.global_config[key])
        else:
            return self.global_config[key]

    def __getattr__(self, item):
        return self.get(item.replace("_", "."))

    def __getitem__(self, item: str) -> str:
        return self.get(item)

    def __setitem__(self, key: str, value: str) -> None:
        return self.set(key, value)

    def get(self, key, default=None) -> str:
        self._initialize_if_static_config_not_set(key)
        return self.global_config.get(key, default)

    def get_all(self) -> dict[str, str]:
        return self.global_config.copy()

    def set(self, key: str, value: str) -> None:
        # Spark Connect sends us only string values, with empty string being
        # equivalent to None.
        if value == "":
            value = None
        self.global_config[key] = value
        if key in self.snowpark_config_mapping.keys():
            snowpark_session = get_or_create_snowpark_session()
            self.snowpark_config_mapping[key](snowpark_session, value)
        # This is necessary to make the configuration available as an attribute.
        setattr(self, key.replace(".", "_"), self._get_config_setting(key))

    def unset(self, key: str) -> None:
        self.global_config.remove(key)

    def is_modifiable(self, key) -> bool:
        self._initialize_if_static_config_not_set(key)
        is_in_config = self.is_set(key)
        is_in_static_config = self.is_static_config(key)
        return is_in_config and not is_in_static_config

    def _initialize_if_static_config_not_set(self, key):
        """
        Spark maintains set of 'static' config values that are immutable.
        SAS allows static configs only to be set once and only if they were never read before.
        This function initializes static configs with default values if they haven't been set.
        """
        if self.is_static_config(key) and not self.is_set(key):
            default_value = self.default_static_global_config[key]
            self.set(key, default_value)
            snowflake_session = get_or_create_snowpark_session()
            set_snowflake_parameters(key, default_value, snowflake_session)

    def is_static_config(self, key):
        return key in self.default_static_global_config.keys()

    def is_set(self, key):
        return key in self.global_config.keys()


SESSION_CONFIG_KEY_WHITELIST = {
    "spark.hadoop.fs.s3a.access.key",
    "spark.hadoop.fs.s3a.secret.key",
    "spark.hadoop.fs.s3a.session.token",
    "spark.sql.execution.pythonUDTF.arrow.enabled",
    "spark.sql.tvf.allowMultipleTableArguments.enabled",
    "snowpark.connect.sql.passthrough",
    "snowpark.connect.cte.optimization_enabled",
    "snowpark.connect.iceberg.external_volume",
    "snowpark.connect.sql.identifiers.auto-uppercase",
    "snowpark.connect.udtf.compatibility_mode",
    "snowpark.connect.views.duplicate_column_names_handling_mode",
    "snowpark.connect.enable_snowflake_extension_behavior",
    "spark.hadoop.fs.s3a.server-side-encryption.key",
    "spark.hadoop.fs.s3a.assumed.role.arn",
    "snowpark.connect.describe_cache_ttl_seconds",
}
AZURE_ACCOUNT_KEY = re.compile(
    r"^fs\.azure\.sas\.[^\.]+\.[^\.]+\.blob\.core\.windows\.net$"
)
AZURE_SAS_KEY = re.compile(
    r"^fs\.azure\.sas\.fixed\.token\.[^\.]+\.dfs\.core\.windows\.net$"
)


def valid_session_config_key(key: str):
    return (
        key in SESSION_CONFIG_KEY_WHITELIST  # AWS session keys
        or AZURE_SAS_KEY.match(key)  # Azure session keys
        or AZURE_ACCOUNT_KEY.match(key)  # Azure account keys
    )


class SessionConfig:
    """This class contains the session configuration for the Spark Server."""

    default_session_config = {
        "snowpark.connect.sql.passthrough": "false",
        "snowpark.connect.cte.optimization_enabled": "false",
        "snowpark.connect.udtf.compatibility_mode": "false",
        "snowpark.connect.views.duplicate_column_names_handling_mode": "rename",
        "spark.sql.execution.pythonUDTF.arrow.enabled": "false",
        "spark.sql.tvf.allowMultipleTableArguments.enabled": "true",
        "snowpark.connect.enable_snowflake_extension_behavior": "false",
        "snowpark.connect.describe_cache_ttl_seconds": "300",
    }

    def __init__(self) -> None:
        self.config = deepcopy(self.default_session_config)
        self.table_metadata: Dict[str, Dict[str, Any]] = {}

    def __getitem__(self, item: str) -> str:
        return self.get(item)

    def __setitem__(self, key: str, value: str) -> None:
        return self.set(key, value)

    def get(self, key, default="") -> str:
        return self.config.get(key, default)

    def set(self, key: str, value: str) -> None:
        if not valid_session_config_key(key):
            return

        self.config[key] = value


CONFIG_ALLOWED_VALUES: dict[str, tuple] = {
    "snowpark.connect.views.duplicate_column_names_handling_mode": (
        "rename",
        "fail",
        "drop",
    ),
    "snowpark.connect.sql.identifiers.auto-uppercase": (
        "all_except_columns",
        "only_columns",
        "all",
        "none",
    ),
}

# Set some default configuration that are necessary for the driver.
global_config = GlobalConfig()
sessions_config: defaultdict[str, SessionConfig] = defaultdict(SessionConfig)


def route_config_proto(
    config: proto_base.ConfigRequest,
    snowpark_session: snowpark.Session,
) -> proto_base.ConfigResponse:
    global global_config
    global sessions_config

    op_type = config.operation.WhichOneof("op_type")
    telemetry.report_config_op_type(op_type)
    match op_type:
        case "set":
            logger.info("SET")
            telemetry.report_config_set(config.operation.set.pairs)
            for pair in config.operation.set.pairs:
                # Check if the value field is present, not present when invalid fields are set in conf.
                if not pair.HasField("value"):
                    from pyspark.errors import IllegalArgumentException

                    exception = IllegalArgumentException(
                        f"Cannot set config '{pair.key}' to None"
                    )
                    attach_custom_error_code(exception, ErrorCodes.INVALID_CONFIG_VALUE)
                    raise exception

                set_config_param(
                    config.session_id, pair.key, pair.value, snowpark_session
                )

            return proto_base.ConfigResponse(session_id=config.session_id)
        case "unset":
            logger.info("UNSET")
            telemetry.report_config_unset(config.operation.unset.keys)
            for key in config.operation.unset.keys:
                unset_config_param(config.session_id, key, snowpark_session)

            return proto_base.ConfigResponse(session_id=config.session_id)
        case "get":
            logger.info("GET")
            res = proto_base.ConfigResponse(session_id=config.session_id)
            telemetry.report_config_get(config.operation.get.keys)
            for key in config.operation.get.keys:
                pair = res.pairs.add()
                pair.key = key
                val = global_config.get(key)
                if val:
                    pair.value = str(val)
            return res
        case "get_with_default":
            logger.info("GET_WITH_DEFAULT")
            telemetry.report_config_get(
                [pair.key for pair in config.operation.get_with_default.pairs]
            )
            result_pairs = [
                proto_base.KeyValue(
                    key=pair.key,
                    value=global_config.get(
                        pair.key, pair.value if pair.HasField("value") else None
                    ),
                )
                for pair in config.operation.get_with_default.pairs
            ]
            return proto_base.ConfigResponse(
                session_id=config.session_id,
                pairs=result_pairs,
            )
        case "get_option":
            logger.info("GET_OPTION")
            res = proto_base.ConfigResponse(session_id=config.session_id)
            telemetry.report_config_get(config.operation.get_option.keys)
            for key in config.operation.get_option.keys:
                pair = res.pairs.add()
                pair.key = key
                val = global_config.get(key, None)
                if val:
                    pair.value = str(val)
            return res
        case "get_all":
            logger.info("GET_ALL")
            res = proto_base.ConfigResponse(session_id=config.session_id)
            prefix = (
                config.operation.get_all.prefix
                if config.operation.get_all.HasField("prefix")
                else None
            )
            config_items = global_config.get_all()
            for item in config_items.items():
                if prefix is None or item[0].startswith(prefix):
                    pair = res.pairs.add()
                    pair.key = (
                        item[0] if prefix is None else item[0].removeprefix(prefix)
                    )
                    if item[1]:
                        pair.value = str(item[1])
            return res
        case "is_modifiable":
            logger.info("IS_MODIFIABLE")
            res = proto_base.ConfigResponse(session_id=config.session_id)
            telemetry.report_config_get(config.operation.is_modifiable.keys)
            for key in config.operation.is_modifiable.keys:
                pair = res.pairs.add()
                pair.key = key
                # Change value to lowercase in order to mimic Java boolean type.
                pair.value = str(global_config.is_modifiable(key)).lower()
            return res
        case _:
            exception = SnowparkConnectNotImplementedError(
                f"Unexpected request {config}"
            )
            attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
            raise exception


def set_config_param(
    session_id: str, key, val, snowpark_session: snowpark.Session
) -> None:
    _verify_static_config_not_modified(key)
    _verify_is_not_readonly_config(key)
    _verify_is_valid_config_value(key, val)

    global_config[key] = val
    if valid_session_config_key(key):
        sessions_config[session_id][key] = val
    set_snowflake_parameters(key, val, snowpark_session)


def unset_config_param(
    session_id: str, key, snowpark_session: snowpark.Session
) -> None:
    _verify_static_config_not_modified(key)

    default_value = global_config.default_global_config.get(key, None)

    # Remove the key from global config
    if default_value is None:
        global_config.unset(key)
    else:
        global_config[key] = default_value

    if valid_session_config_key(key):
        default_session_value = SessionConfig.default_session_config.get(key, "")
        sessions_config[session_id].set(key, default_session_value)

    set_snowflake_parameters(key, default_value, snowpark_session)


def _verify_static_config_not_modified(key: str) -> None:
    # https://github.com/apache/spark/blob/v3.5.3/sql/core/src/main/scala/org/apache/spark/sql/RuntimeConfig.scala#L161
    # Spark does not allow to modify static configurations at runtime.
    if global_config.is_static_config(key) and global_config.is_set(key):
        exception = ValueError(f"Cannot modify the value of a static config: {key}")
        attach_custom_error_code(exception, ErrorCodes.CONFIG_CHANGE_NOT_ALLOWED)
        raise exception


def _verify_is_valid_config_value(key: str, value: Any) -> None:
    if key in CONFIG_ALLOWED_VALUES and value not in CONFIG_ALLOWED_VALUES[key]:
        exception = ValueError(
            f"Invalid value '{value}' for key '{key}'. Allowed values: {', '.join(CONFIG_ALLOWED_VALUES[key])}."
        )
        attach_custom_error_code(exception, ErrorCodes.INVALID_CONFIG_VALUE)
        raise exception


def _verify_is_not_readonly_config(key):
    if key in global_config.readonly_config_list:
        exception = ValueError(
            f"Config with key {key} is read-only and cannot be modified."
        )
        attach_custom_error_code(exception, ErrorCodes.CONFIG_CHANGE_NOT_ALLOWED)
        raise exception


def set_jvm_timezone(timezone_id: str):
    """
    Set JVM default timezone at runtime (after JVM startup).

    Args:
        timezone_id: Timezone ID like 'America/New_York', 'UTC', 'Europe/London'

    Returns:
        bool: True if successfully set

    Raises:
        RuntimeError: If JVM is not started
    """
    if not jpype.isJVMStarted():
        exception = RuntimeError("JVM must be started before setting timezone")
        attach_custom_error_code(exception, ErrorCodes.INTERNAL_ERROR)
        raise exception

    try:
        with get_jpype_jclass_lock():
            TimeZone = jpype.JClass("java.util.TimeZone")
        new_timezone = TimeZone.getTimeZone(timezone_id)
        TimeZone.setDefault(new_timezone)

        logger.info(f"JVM timezone changed to: {new_timezone.getID()}")
    except Exception as e:
        logger.error(f"Failed to set JVM timezone: {e}")


def reset_jvm_timezone_to_system_default():
    """Reset JVM timezone to the system's default timezone"""
    if not jpype.isJVMStarted():
        exception = RuntimeError("JVM must be started first")
        attach_custom_error_code(exception, ErrorCodes.INTERNAL_ERROR)
        raise exception

    try:
        TimeZone = jpype.JClass("java.util.TimeZone")
        TimeZone.setDefault(None)
        logger.info(
            f"Reset JVM timezone to system default: {TimeZone.getDefault().getID()}"
        )
    except jpype.JException as e:
        exception = RuntimeError(f"Java exception while resetting timezone: {e}")
        attach_custom_error_code(exception, ErrorCodes.INTERNAL_ERROR)
        raise exception
    except Exception as e:
        exception = RuntimeError(f"Unexpected error resetting JVM timezone: {e}")
        attach_custom_error_code(exception, ErrorCodes.INTERNAL_ERROR)
        raise exception


def set_snowflake_parameters(
    key: str, value: Any, snowpark_session: snowpark.Session
) -> None:
    match key:
        case "spark.sql.session.timeZone":
            if value:
                snowpark_session.sql(
                    f"ALTER SESSION SET TIMEZONE = '{value}'"
                ).collect()
            else:
                snowpark_session.sql("ALTER SESSION UNSET TIMEZONE").collect()
        case "spark.sql.globalTempDatabase":
            if not value:
                value = global_config.default_static_global_config.get(key)

            snowpark_name = quote_name_without_upper_casing(value)
            if auto_uppercase_non_column_identifiers():
                snowpark_name = snowpark_name.upper()

            # Create the schema on demand. Before creating it, however,
            # check if it already exists, to handle the case where the schema exists
            # but the user does not have permissions to execute `CREATE SCHEMA`.
            try:
                snowpark_session.sql(
                    "DESC SCHEMA identifier(?)", [snowpark_name]
                ).collect()
            except SnowparkSQLException:
                db = snowpark_session.get_current_database()
                prev_schema = snowpark_session.get_current_schema()
                # Even though we checked that the schema doesn't exist,
                # use "IF NOT EXISTS" to avoid race conditions.
                snowpark_session.sql(
                    "CREATE SCHEMA IF NOT EXISTS identifier(?)", [snowpark_name]
                ).collect()
                # When schema is created, it is also changed in the context of the session
                match (prev_schema, snowpark_session.get_current_schema()):
                    case (None, curr) if curr is not None:
                        # session.use_schema(None) is not allowed.
                        # Instead, we call `use_database` which will set schema in context to the default one.
                        snowpark_session.use_database(db)
                    case (prev, curr) if prev != curr:
                        snowpark_session.use_schema(prev)
        case "snowpark.connect.cte.optimization_enabled":
            # Set CTE optimization on the snowpark session
            cte_enabled = str_to_bool(value)
            snowpark_session.cte_optimization_enabled = cte_enabled
            logger.info(f"Updated snowpark session CTE optimization: {cte_enabled}")
        case "snowpark.connect.structured_types.fix":
            # TODO: SNOW-2367714 Remove this once the fix is automatically enabled in Snowpark
            snowpark.context._enable_fix_2360274 = str_to_bool(value)
            logger.info(f"Updated snowpark session structured types fix: {value}")
        case _:
            pass


def get_boolean_session_config_param(name: str) -> bool:
    session_config = sessions_config[get_session_id()]
    return str_to_bool(session_config[name])


def get_string_session_config_param(name: str) -> str:
    session_config = sessions_config[get_session_id()]
    return str(session_config[name])


def get_cte_optimization_enabled() -> bool:
    """Get the CTE optimization configuration setting."""
    return get_boolean_session_config_param("snowpark.connect.cte.optimization_enabled")


def get_describe_cache_ttl_seconds() -> int:
    """Get the describe query cache TTL from session config, with a default fallback."""
    session_config: SessionConfig = sessions_config[get_session_id()]
    default_ttl: str = SessionConfig.default_session_config[
        "snowpark.connect.describe_cache_ttl_seconds"
    ]
    try:
        ttl_str = session_config.get(
            "snowpark.connect.describe_cache_ttl_seconds", default_ttl
        )
        return int(ttl_str)
    except ValueError:  # fallback to default ttl
        return int(default_ttl)


def auto_uppercase_column_identifiers() -> bool:
    session_config = sessions_config[get_session_id()]
    auto_upper_case_config = session_config[
        "snowpark.connect.sql.identifiers.auto-uppercase"
    ]
    if auto_upper_case_config:
        return auto_upper_case_config.lower() in ("all", "only_columns")

    return not global_config.spark_sql_caseSensitive


def auto_uppercase_non_column_identifiers() -> bool:
    session_config = sessions_config[get_session_id()]
    auto_upper_case_config = session_config[
        "snowpark.connect.sql.identifiers.auto-uppercase"
    ]
    if auto_upper_case_config:
        return auto_upper_case_config.lower() in ("all", "all_except_columns")

    return not global_config.spark_sql_caseSensitive


def parse_imports(session: snowpark.Session, imports: str | None) -> None:
    if not imports:
        return

    # UDF needs to be recreated to include new imports
    clear_external_udxf_cache(session)

    for udf_import in imports.strip("[] ").split(","):
        session.add_import(udf_import)


def get_timestamp_type():
    match global_config["spark.sql.timestampType"]:
        case "TIMESTAMP_LTZ":
            timestamp_type = TimestampType(TimestampTimeZone.LTZ)
        case "TIMESTAMP_NTZ":
            timestamp_type = TimestampType(TimestampTimeZone.NTZ)
        case _:
            # shouldn't happen since `spark.sql.timestampType` is always defined, and `spark.conf.unset` sets it to default (TIMESTAMP_LTZ)
            timestamp_type = TimestampType(TimestampTimeZone.LTZ)
    return timestamp_type


def record_table_metadata(
    table_identifier: str,
    table_type: str,
    data_source: str,
    supports_column_rename: bool = True,
) -> None:
    """
    Record metadata about a table for Spark compatibility checks.

    Args:
        table_identifier: Full table identifier (catalog.database.table)
        table_type: "v1" or "v2"
        data_source: Source format (parquet, csv, iceberg, etc.)
        supports_column_rename: Whether the table supports RENAME COLUMN
    """
    session_id = get_session_id()
    session_config = sessions_config[session_id]

    # Normalize table identifier for consistent lookup
    # Use the full catalog.database.table identifier to avoid conflicts
    normalized_identifier = table_identifier.upper().strip('"')

    session_config.table_metadata[normalized_identifier] = {
        "table_type": table_type,
        "data_source": data_source,
        "supports_column_rename": supports_column_rename,
    }


def get_table_metadata(table_identifier: str) -> Dict[str, Any] | None:
    """
    Get stored metadata for a table.

    Args:
        table_identifier: Full table identifier (catalog.database.table)

    Returns:
        Table metadata dict or None if not found
    """
    session_id = get_session_id()
    session_config = sessions_config[session_id]

    normalized_identifier = unquote_if_quoted(table_identifier).upper()

    return session_config.table_metadata.get(normalized_identifier)


def check_table_supports_operation(table_identifier: str, operation: str) -> bool:
    """
    Check if a table supports a given operation based on metadata and config.

    Args:
        table_identifier: Full table identifier (catalog.database.table)
        operation: Operation to check (e.g., "rename_column")

    Returns:
        True if operation is supported, False if should be blocked
    """
    table_metadata = get_table_metadata(table_identifier)

    if not table_metadata:
        return True

    session_id = get_session_id()
    session_config = sessions_config[session_id]
    enable_extensions = str_to_bool(
        session_config.get(
            "snowpark.connect.enable_snowflake_extension_behavior", "false"
        )
    )

    if enable_extensions:
        return True

    if operation == "rename_column":
        return table_metadata.get("supports_column_rename", True)

    return True
