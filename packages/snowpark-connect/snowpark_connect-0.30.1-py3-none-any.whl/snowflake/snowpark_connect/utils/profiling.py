#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

# Some basic profiling that is enabled with env variable SNOWPARK_CONNECT_ENABLE_PROFILING = 1
# By default, profiles are written for each annotated method into /tmp/snowpark_connect_profiles, this is
# controlled by SNOWPARK_CONNECT_PROFILE_OUTPUT_DIR
#
# By shipping this, we can ask customers/partners to create a profile for us to investigate further if needed.

import cProfile
import functools
import os
from datetime import datetime
from typing import Any, Callable

PROFILING_ENABLED = os.environ.get("SNOWPARK_CONNECT_ENABLE_PROFILING", "0") == "1"
PROFILE_OUTPUT_DIR = os.environ.get(
    "SNOWPARK_CONNECT_PROFILE_OUTPUT_DIR", "/tmp/snowpark_connect_profiles"
)


def profile_method(method: Callable) -> Callable:
    """Decorator to profile a specific method."""

    @functools.wraps(method)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not PROFILING_ENABLED:
            return method(*args, **kwargs)

        os.makedirs(PROFILE_OUTPUT_DIR, exist_ok=True)

        method_name = method.__name__
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        profile_filename = f"{PROFILE_OUTPUT_DIR}/{method_name}_{timestamp}.prof"

        profiler = cProfile.Profile()
        profiler.enable()

        try:
            result = method(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            profiler.dump_stats(profile_filename)

    return wrapper
