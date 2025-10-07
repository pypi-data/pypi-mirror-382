#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
import pathlib
import threading
import time

from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger

_resources_initialized = threading.Event()
_initializer_lock = threading.Lock()
SPARK_VERSION = "3.5.6"
RESOURCE_PATH = "/snowflake/snowpark_connect/resources"
_upload_jars = True  # Flag to control whether to upload jars. Required for Scala UDFs.


def initialize_resources() -> None:
    """Initialize all expensive resources. We should initialize what we can here, so that actual rpc calls like
    ExecutePlan are as fast as possible."""
    from snowflake.snowpark import functions as snowpark_fn
    from snowflake.snowpark_connect.expression.map_sql_expression import sql_parser

    session = get_or_create_snowpark_session()

    # This could be merged into the sql_parser call, it is done separately because
    # it introduces additional overhead. This finer grained structuring allows us to make finer grained
    # preloading decisions.
    def warm_sql_parser() -> None:
        parser = sql_parser()
        parser.parseExpression("1 + 1")
        parser.parseExpression("CASE WHEN id > 10 THEN 'large' ELSE 'small' END")

    def initialize_session_stage() -> None:
        _ = session.get_session_stage()

    def initialize_catalog() -> None:
        _ = session.catalog

    def warm_up_sf_connection() -> None:
        df = session.create_dataframe([["a", 3], ["b", 2], ["a", 1]], schema=["x", "y"])
        df = df.select(snowpark_fn.upper(df.x).alias("x"), df.y.alias("y2"))
        df = df.group_by(df.x).agg(snowpark_fn.sum("y2"))
        df.collect()

        session.sql("select 1 as sf_connection_warm_up").collect()

    def upload_scala_udf_jars() -> None:
        """Upload Spark jar files required for creating Scala UDFs."""
        stage = session.get_session_stage()
        resource_path = stage + RESOURCE_PATH
        import snowflake

        pyspark_jars = (
            pathlib.Path(snowflake.snowpark_connect.__file__).parent / "includes/jars"
        )
        jar_files = [
            f"spark-sql_2.12-{SPARK_VERSION}.jar",
            f"spark-connect-client-jvm_2.12-{SPARK_VERSION}.jar",
            f"spark-common-utils_2.12-{SPARK_VERSION}.jar",
            "sas-scala-udf_2.12-0.1.0.jar",
            "json4s-ast_2.12-3.7.0-M11.jar",
        ]

        for jar in jar_files:
            session.file.put(
                str(pyspark_jars) + "/" + jar,
                resource_path,
                auto_compress=False,
                overwrite=False,
                source_compression="NONE",
            )

    start_time = time.time()

    resources = [
        ("SQL Parser Init", sql_parser),  # Takes about 0.5s
        ("SQL Parser Warm Up", warm_sql_parser),  # Takes about 0.7s
        ("Initialize Session Stage", initialize_session_stage),  # Takes about 0.3s
        ("Initialize Session Catalog", initialize_catalog),  # Takes about 1.2s
        ("Snowflake Connection Warm Up", warm_up_sf_connection),  # Takes about 1s
    ]

    if _upload_jars:
        resources.append(("Upload Scala UDF Jars", upload_scala_udf_jars))

    for name, resource_func in resources:
        resource_start = time.time()
        try:
            resource_func()
            logger.info(f"Initialized {name} in {time.time() - resource_start:.2f}s")
        except Exception as e:
            # We will only log the error if it isn't caused by session being closed. Session
            # closed error happens when the particular run finishes very quickly.
            if str(e).find("because the session has been closed") == -1:
                logger.error(f"Failed to initialize {name}: {e}")

    _resources_initialized.set()
    logger.info(f"All resources initialized in {time.time() - start_time:.2f}s")


_resource_initializer = threading.Thread(
    target=initialize_resources, name="ResourceInitializer"
)


def initialize_resources_async() -> threading.Thread:
    """Start resource initialization in background."""
    with _initializer_lock:
        if not _resource_initializer.is_alive() and _resource_initializer.ident is None:
            _resource_initializer.start()
        return _resource_initializer


def wait_for_resource_initialization() -> None:
    with _initializer_lock:
        _resource_initializer.join(timeout=300)  # wait at most 300 seconds
    if _resource_initializer.is_alive():
        logger.error(
            "Resource initialization failed - initializer thread has been running for over 300 seconds."
        )
        raise RuntimeError(
            "Resource initialization failed - initializer thread has been running for over 300 seconds."
        )


def set_upload_jars(upload: bool) -> None:
    """Set whether to upload jars required for Scala UDFs. This should be set to False if Scala UDFs
    are not used, to avoid the overhead of uploading jars."""
    global _upload_jars
    _upload_jars = upload
