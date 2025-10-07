#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from collections import defaultdict

from snowflake.connector.errors import ProgrammingError
from snowflake.snowpark_connect.relation.catalogs import CATALOGS, SNOWFLAKE_CATALOG
from snowflake.snowpark_connect.relation.catalogs.abstract_spark_catalog import (
    AbstractSparkCatalog,
)
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session

CURRENT_CATALOG = SNOWFLAKE_CATALOG
CURRENT_CATALOG_NAME: str | None = "spark_catalog"
CATALOG_TEMP_OBJECTS: defaultdict[
    str | None, set[tuple[str | None, str | None, str]]
] = defaultdict(set)


def get_current_catalog() -> AbstractSparkCatalog:
    return CURRENT_CATALOG


def set_current_catalog(catalog_name: str | None) -> AbstractSparkCatalog:
    global CURRENT_CATALOG_NAME

    # Validate input parameters to match PySpark behavior
    if catalog_name is None:
        raise ValueError("Catalog name cannot be None")
    if catalog_name == "":
        raise ValueError(
            "Catalog '' plugin class not found: spark.sql.catalog. is not defined"
        )

    CURRENT_CATALOG_NAME = catalog_name
    if catalog_name in CATALOGS:
        return CATALOGS[catalog_name]

    sf_catalog = get_or_create_snowpark_session().catalog
    try:
        sf_catalog.setCurrentDatabase(catalog_name if catalog_name is not None else "")
        return get_current_catalog()
    except ProgrammingError as e:
        raise Exception(
            f"Catalog '{catalog_name}' plugin class not found: spark.sql.catalog.{catalog_name} is not defined"
        ) from e


def _get_current_temp_objects() -> set[tuple[str | None, str | None, str]]:
    return CATALOG_TEMP_OBJECTS[CURRENT_CATALOG_NAME]
