#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#


class SnowparkConnectException(Exception):
    """Parent class to all SnowparkConnect related exceptions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class MissingDatabase(SnowparkConnectException):
    def __init__(self) -> None:
        super().__init__(
            "No default database found in session",
        )


class MissingSchema(SnowparkConnectException):
    def __init__(self) -> None:
        super().__init__(
            "No default schema found in session",
        )


class MaxRetryExceeded(SnowparkConnectException):
    ...
