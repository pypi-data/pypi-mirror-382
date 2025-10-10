#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import logging

from pyspark import StorageLevel

logger = logging.getLogger("snowflake_connect_server")
logger.setLevel(logging.WARN)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s"
)
console_handler.setFormatter(formatter)
# Display the logs to the console
logger.addHandler(console_handler)


def run_once_decorator(func):
    def wrapper(*args, **kwargs):
        if not hasattr(wrapper, "has_run"):
            wrapper.has_run = True
            return func(*args, **kwargs)

    return wrapper


@run_once_decorator
def log_waring_once_storage_level(storage_level: StorageLevel):
    logger.warning(
        f"Ignored unsupported Spark storage level:\n{storage_level}"
        "Snowflake will always create materialized temp table from the dataframe "
        "when dataframe.cache or dataframe.persist is called.\n"
        "The behavior is similar with Spark's StorageLevel.DISK_ONLY."
    )
