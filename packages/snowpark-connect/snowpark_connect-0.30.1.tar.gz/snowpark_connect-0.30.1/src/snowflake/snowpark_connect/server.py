#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

# Some content in this file is derived from Apache Spark. In accordance
# with Apache 2 license, the license for Apache Spark is as follows:
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import atexit
import logging
import os
import pathlib
import socket
import tempfile
import threading
import urllib.parse
import zipfile
from concurrent import futures
from typing import Any, Callable, Dict, List, Optional, Tuple

import grpc
import jpype
import pyspark
import pyspark.sql.connect.proto.base_pb2 as proto_base
import pyspark.sql.connect.proto.base_pb2_grpc as proto_base_grpc
import pyspark.sql.connect.proto.common_pb2 as common_proto
import pyspark.sql.connect.proto.relations_pb2 as relations_proto
import pyspark.sql.connect.proto.types_pb2 as types_proto
from packaging import version
from pyspark import StorageLevel
from pyspark.conf import SparkConf
from pyspark.errors import PySparkValueError
from pyspark.sql.connect.client.core import ChannelBuilder
from pyspark.sql.connect.session import SparkSession

import snowflake.snowpark_connect
import snowflake.snowpark_connect.proto.control_pb2_grpc as control_grpc
import snowflake.snowpark_connect.tcm as tcm
from snowflake import snowpark
from snowflake.snowpark_connect.analyze_plan.map_tree_string import map_tree_string
from snowflake.snowpark_connect.config import route_config_proto
from snowflake.snowpark_connect.constants import SERVER_SIDE_SESSION_ID
from snowflake.snowpark_connect.control_server import ControlServicer
from snowflake.snowpark_connect.error.error_utils import build_grpc_error_response
from snowflake.snowpark_connect.execute_plan.map_execution_command import (
    map_execution_command,
)
from snowflake.snowpark_connect.execute_plan.map_execution_root import (
    map_execution_root,
)
from snowflake.snowpark_connect.relation.map_local_relation import map_local_relation
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.relation.utils import get_semantic_string
from snowflake.snowpark_connect.resources_initializer import initialize_resources_async
from snowflake.snowpark_connect.type_mapping import (
    map_type_string_to_proto,
    snowpark_to_proto_type,
)
from snowflake.snowpark_connect.utils.artifacts import (
    check_checksum,
    write_artifact,
    write_class_files_to_stage,
)
from snowflake.snowpark_connect.utils.cache import (
    df_cache_map_get,
    df_cache_map_pop,
    df_cache_map_put_if_absent,
)
from snowflake.snowpark_connect.utils.context import (
    clear_context_data,
    get_session_id,
    set_session_id,
    set_spark_version,
)
from snowflake.snowpark_connect.utils.env_utils import get_int_from_env
from snowflake.snowpark_connect.utils.external_udxf_cache import (
    clear_external_udxf_cache,
)
from snowflake.snowpark_connect.utils.interrupt import (
    interrupt_all_queries,
    interrupt_queries_with_tag,
    interrupt_query,
)
from snowflake.snowpark_connect.utils.profiling import profile_method
from snowflake.snowpark_connect.utils.session import (
    configure_snowpark_session,
    get_or_create_snowpark_session,
    set_query_tags,
)
from snowflake.snowpark_connect.utils.snowpark_connect_logging import (
    log_waring_once_storage_level,
    logger,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
    telemetry,
)
from snowflake.snowpark_connect.utils.xxhash64 import xxhash64_string

DEFAULT_PORT = 15002

# https://github.com/apache/spark/blob/v3.5.3/connector/connect/common/src/main/scala/org/apache/spark/sql/connect/common/config/ConnectCommon.scala#L21
_SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE = 128 * 1024 * 1024
# TODO: Verify if we we want to configure it via env variables.
_SPARK_CONNECT_GRPC_MAX_METADATA_SIZE = 64 * 1024  # 64kb


def _sanitize_file_paths(text: str) -> str:
    """
    Sanitize file paths in error messages by replacing them with placeholders.
    Only matches actual file paths, not module names or class names.
    """
    import re

    # Pattern to match file paths in traceback "File" lines only
    # This targets the specific format: File "/path/to/file.py", line XX
    file_line_pattern = r'(File\s+["\'])([^"\']+)(["\'],\s+line\s+\d+)'

    def replace_file_path(match):
        return f"{match.group(1)}<redacted_file_path>{match.group(3)}"

    return re.sub(file_line_pattern, replace_file_path, text)


def _handle_exception(context, e: Exception):
    import traceback

    # traceback.print_exc()
    # SNOWFLAKE_SHOW_ERROR_TRACE controls sanitized traceback printing (default: false)
    show_traceback = os.getenv("SNOWFLAKE_SHOW_ERROR_TRACE", "false").lower() == "true"

    if show_traceback:
        # Show detailed traceback (includes error info naturally)
        error_traceback = traceback.format_exc()
        sanitized_traceback = _sanitize_file_paths(error_traceback)
        logger.error(sanitized_traceback)
    else:
        # Show only basic error information, no traceback
        logger.error("Error: %s - %s", type(e).__name__, str(e))

    telemetry.report_request_failure(e)

    if tcm.TCM_MODE:
        # TODO: SNOW-2009834 gracefully return error back in TCM
        raise e

    from grpc_status import rpc_status

    rich_status = build_grpc_error_response(e)
    context.abort_with_status(rpc_status.to_status(rich_status))


class SnowflakeConnectServicer(proto_base_grpc.SparkConnectServiceServicer):
    def __init__(
        self,
        log_request_fn: Optional[Callable[[bytearray], None]] = None,
    ) -> None:
        self.log_request_fn = log_request_fn
        # Trigger async initialization here, so that we reduce overhead for rpc calls.
        initialize_resources_async()

    @profile_method
    def ExecutePlan(self, request: proto_base.ExecutePlanRequest, context):
        """Executes a request that contains the query and returns a stream of [[Response]].

        It is guaranteed that there is at least one ARROW batch returned even if the result set is empty.
        """
        logger.info("ExecutePlan")
        if self.log_request_fn is not None:
            self.log_request_fn(request.SerializeToString())

        # TODO: remove session id context when we host this in Snowflake server
        # set the thread-local context of session id
        clear_context_data()
        set_session_id(request.session_id)
        set_spark_version(request.client_type)
        telemetry.initialize_request_summary(request)

        set_query_tags(request.tags)

        result_iter = iter(())
        try:
            match request.plan.WhichOneof("op_type"):
                case "root":
                    logger.info("ROOT")
                    result_iter = map_execution_root(request)
                case "command":
                    logger.info("COMMAND")
                    command_result = map_execution_command(request)
                    if command_result is not None:
                        result_iter = iter([command_result])

            yield from result_iter
            yield proto_base.ExecutePlanResponse(
                session_id=request.session_id,
                operation_id=SERVER_SIDE_SESSION_ID,
                result_complete=proto_base.ExecutePlanResponse.ResultComplete(),
            )
        except Exception as e:
            _handle_exception(context, e)
        finally:
            telemetry.send_request_summary_telemetry()

    @profile_method
    def AnalyzePlan(self, request: proto_base.AnalyzePlanRequest, context):
        """Analyzes a query and returns a [[AnalyzeResponse]] containing metadata about the query."""
        logger.info(f"AnalyzePlan: {request.WhichOneof('analyze')}")
        if self.log_request_fn is not None:
            self.log_request_fn(request.SerializeToString())
        try:
            # TODO: remove session id context when we host this in Snowflake server
            # set the thread-local context of session id
            clear_context_data()
            set_session_id(request.session_id)
            set_spark_version(request.client_type)
            telemetry.initialize_request_summary(request)
            match request.WhichOneof("analyze"):
                case "schema":
                    result = map_relation(request.schema.plan.root)

                    from snowflake.snowpark_connect.relation.read.metadata_utils import (
                        filter_metadata_columns,
                    )

                    filtered_result = filter_metadata_columns(result)
                    filtered_df = filtered_result.dataframe

                    schema = proto_base.AnalyzePlanResponse.Schema(
                        schema=types_proto.DataType(
                            **snowpark_to_proto_type(
                                filtered_df.schema,
                                filtered_result.column_map,
                                filtered_df,
                            )
                        )
                    )
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        schema=schema,
                    )
                case "tree_string":
                    return map_tree_string(request)
                case "is_local":
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        is_local=proto_base.AnalyzePlanResponse.IsLocal(is_local=False),
                    )
                case "ddl_parse":
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        ddl_parse=proto_base.AnalyzePlanResponse.DDLParse(
                            parsed=map_type_string_to_proto(
                                request.ddl_parse.ddl_string
                            )
                        ),
                    )
                case "get_storage_level":
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        get_storage_level=proto_base.AnalyzePlanResponse.GetStorageLevel(
                            storage_level=common_proto.StorageLevel(
                                use_disk=True, use_memory=True
                            )
                        ),
                    )
                case "persist":
                    plan_id = request.persist.relation.common.plan_id
                    # cache the plan if it is not already in the map

                    df_cache_map_put_if_absent(
                        (request.session_id, plan_id),
                        lambda: map_relation(request.persist.relation),
                        materialize=True,
                    )

                    storage_level = request.persist.storage_level
                    if storage_level != StorageLevel.DISK_ONLY:
                        log_waring_once_storage_level(storage_level)

                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        persist=proto_base.AnalyzePlanResponse.Persist(),
                    )
                case "unpersist":
                    plan_id = request.persist.relation.common.plan_id
                    # unpersist the cached plan
                    df_cache_map_pop((request.session_id, plan_id))

                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        unpersist=proto_base.AnalyzePlanResponse.Unpersist(),
                    )
                case "explain":
                    # Snowflake only exposes simplified execution plans, similar to Spark's optimized logical plans.
                    # Snowpark provides the execution plan IFF the dataframe maps to a single query.
                    # TODO: Do we need to return a Spark-like plan?
                    result = map_relation(request.explain.plan.root)
                    snowpark_df = result.dataframe
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        explain=proto_base.AnalyzePlanResponse.Explain(
                            explain_string=snowpark_df._explain_string()
                        ),
                    )
                case "spark_version":
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        spark_version=proto_base.AnalyzePlanResponse.SparkVersion(
                            version=pyspark.__version__
                        ),
                    )
                case "same_semantics":
                    target_queries_hash = xxhash64_string(
                        get_semantic_string(request.same_semantics.target_plan.root)
                    )
                    other_queries_hash = xxhash64_string(
                        get_semantic_string(request.same_semantics.other_plan.root)
                    )
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        same_semantics=proto_base.AnalyzePlanResponse.SameSemantics(
                            result=target_queries_hash == other_queries_hash
                        ),
                    )
                case "semantic_hash":
                    queries_str = get_semantic_string(request.semantic_hash.plan.root)
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        semantic_hash=proto_base.AnalyzePlanResponse.SemanticHash(
                            result=xxhash64_string(queries_str)
                            & 0x7FFFFFFF  # need a 32 bit int here.
                        ),
                    )
                case "is_streaming":
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        is_streaming=proto_base.AnalyzePlanResponse.IsStreaming(
                            is_streaming=False
                        ),
                    )
                case "input_files":
                    files = []
                    if request.input_files.plan.root.HasField("read"):
                        files = _get_files_metadata(
                            request.input_files.plan.root.read.data_source
                        )
                    elif request.input_files.plan.root.HasField("join"):
                        left_files = _get_files_metadata(
                            request.input_files.plan.root.join.left.read.data_source
                        )
                        right_files = _get_files_metadata(
                            request.input_files.plan.root.join.right.read.data_source
                        )
                        files = left_files + right_files
                    return proto_base.AnalyzePlanResponse(
                        session_id=request.session_id,
                        input_files=proto_base.AnalyzePlanResponse.InputFiles(
                            files=list(set(files))
                        ),
                    )
                case _:
                    raise SnowparkConnectNotImplementedError(
                        f"ANALYZE PLAN NOT IMPLEMENTED:\n{request}"
                    )
        except Exception as e:
            _handle_exception(context, e)
        finally:
            telemetry.send_request_summary_telemetry()

    @staticmethod
    def Config(
        request: proto_base.ConfigRequest,
        context,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        """Update or fetch the configurations and returns a [[ConfigResponse]] containing the result."""
        logger.info("Config")
        try:
            telemetry.initialize_request_summary(request)
            return route_config_proto(request, get_or_create_snowpark_session())
        except Exception as e:
            _handle_exception(context, e)
        finally:
            telemetry.send_request_summary_telemetry()

    def AddArtifacts(self, request_iterator, context):
        """Add artifacts to the session and returns a [[AddArtifactsResponse]] containing metadata about
        the added artifacts.
        """
        logger.info("AddArtifacts")
        session: snowpark.Session = get_or_create_snowpark_session()
        filenames: dict[str, str] = {}
        response: dict[str, proto_base.AddArtifactsResponse.ArtifactSummary] = {}
        # Store accumulated data for local relation cache
        cache_data: dict[str, bytearray] = {}

        def _try_handle_local_relation(artifact_name: str, data: bytes):
            """
            Attempt to deserialize the artifact data to a LocalRelation protobuf message.
            LocalRelation messages represent in-memory data that should be materialized
            in temporary table in Snowflake rather than stored as file artifact.
             - If successful: creates a temporary table and caches the DataFrame in `df_cache_map`
             - If unsuccessful: falls back to storing as a regular file artifact
            """

            is_likely_local_relation = artifact_name.startswith(
                "cache/"
            )  # heuristic to identify local relations

            def _handle_regular_artifact():
                filenames[artifact_name] = write_artifact(
                    session,
                    artifact_name,
                    data,
                    overwrite=True,
                )

            if is_likely_local_relation:
                try:
                    l_relation = relations_proto.LocalRelation()
                    l_relation.ParseFromString(data)
                    relation = relations_proto.Relation(local_relation=l_relation)
                    df_cache_map_put_if_absent(
                        (get_session_id(), artifact_name.replace("cache/", "")),
                        lambda: map_local_relation(relation),  # noqa: B023
                        materialize=True,
                    )
                except Exception as e:
                    logger.warning("Failed to put df into cache: %s", str(e))
                    # fallback - treat as regular artifact
                    _handle_regular_artifact()
            else:
                # Not a LocalRelation - treat as regular artifact
                _handle_regular_artifact()

        # Spark sends artifacts as iterators that are either chunked or a full batch.
        #
        # Chunked artifacts start with a "begin_chunk" followed by a series of "chunk"
        # messages. The "chunk" messages do not contain a name, so we store the name
        # in `current_name` so we can append all the chunks to the same object.
        # Chunked artifacts are written incrementally as gzip files to reduce memory
        # issues.
        #
        # Batch artifacts are sent as a single "batch" message containing a list of
        # artifacts. We do not need to keep track of the name since it is included in
        # each artifact.
        current_name: str = ""
        for request in request_iterator:
            clear_context_data()
            set_session_id(request.session_id)
            set_spark_version(request.client_type)
            match request.WhichOneof("payload"):
                case "begin_chunk":
                    current_name = request.begin_chunk.name
                    assert (
                        current_name not in filenames
                    ), "Duplicate artifact name found."

                    if current_name.startswith("cache/"):
                        cache_data[current_name] = bytearray(
                            request.begin_chunk.initial_chunk.data
                        )
                    else:
                        filenames[current_name] = write_artifact(
                            session,
                            current_name,
                            request.begin_chunk.initial_chunk.data,
                            overwrite=True,
                        )
                    response[
                        current_name
                    ] = proto_base.AddArtifactsResponse.ArtifactSummary(
                        name=current_name,
                        is_crc_successful=check_checksum(
                            request.begin_chunk.initial_chunk.data,
                            request.begin_chunk.initial_chunk.crc,
                        ),
                    )
                case "chunk":
                    if current_name.startswith("cache/"):
                        cache_data[current_name].extend(request.chunk.data)
                    else:
                        assert filenames[current_name] == write_artifact(
                            session, current_name, request.chunk.data
                        ), "Artifact staging error."

                    response[
                        current_name
                    ] = proto_base.AddArtifactsResponse.ArtifactSummary(
                        name=current_name,
                        is_crc_successful=response[current_name].is_crc_successful
                        and check_checksum(request.chunk.data, request.chunk.crc),
                    )
                case "batch":
                    for artifact in request.batch.artifacts:
                        data = artifact.data.data

                        _try_handle_local_relation(artifact.name, data)
                        response[
                            artifact.name
                        ] = proto_base.AddArtifactsResponse.ArtifactSummary(
                            name=artifact.name,
                            is_crc_successful=check_checksum(
                                artifact.data.data, artifact.data.crc
                            ),
                        )
                case _:
                    raise ValueError(
                        f"Unexpected payload type in AddArtifacts: {request.WhichOneof('payload')}"
                    )

        for name, data in cache_data.items():
            _try_handle_local_relation(name, bytes(data))

        class_files: dict[str, str] = {}
        for (name, filepath) in filenames.items():
            if name.endswith(".class"):
                # name is <dir>/<package>/<class_name>
                # we don't need the dir name, but require the package, so only remove dir
                if os.name != "nt":
                    class_files[name.split("/", 1)[-1]] = filepath
                else:
                    class_files[name.split("\\", 1)[-1]] = filepath
                continue
            session.file.put(
                filepath,
                session.get_session_stage(),
                auto_compress=False,
                overwrite=True,
                source_compression="GZIP" if name.endswith(".gz") else "NONE",
            )

            if name.startswith("cache"):
                continue

            # Remove temporary stored files which are put on the stage
            os.remove(filepath)

            # Add only files marked to be used in user generated Python UDFs.
            cached_name = f"{session.get_session_stage()}/{filepath.split('/')[-1]}"
            if not name.startswith("pyfiles") and cached_name in session._python_files:
                session._python_files.remove(cached_name)
            elif name.startswith("pyfiles"):
                session._python_files.add(cached_name)

            if not name.startswith("pyfiles"):
                session._import_files.add(cached_name)

        if class_files:
            write_class_files_to_stage(session, class_files)

        if any(not name.startswith("cache") for name in filenames.keys()):
            clear_external_udxf_cache(session)

        return proto_base.AddArtifactsResponse(artifacts=list(response.values()))

    def ArtifactStatus(self, request, context):
        """Check statuses of artifacts in the session and returns them in a [[ArtifactStatusesResponse]]"""
        logger.info("ArtifactStatus")
        clear_context_data()
        set_session_id(request.session_id)
        set_spark_version(request.client_type)
        session: snowpark.Session = get_or_create_snowpark_session()
        if os.name != "nt":
            tmp_path = f"/tmp/sas-{session.session_id}/"
        else:
            tmp_path = f"{tempfile.gettempdir()}/sas-{session.session_id}/"

        def _is_local_relation_cached(name: str) -> bool:
            if name.startswith("cache/"):
                hash = name.replace("cache/", "")
                cached_df = df_cache_map_get((get_session_id(), hash))
                return cached_df is not None
            return False

        files = []
        for _, _, filenames in os.walk(tmp_path):
            for filename in filenames:
                files.append(filename)
        if len(files) == 0:
            statuses = {
                name: proto_base.ArtifactStatusesResponse.ArtifactStatus(
                    exists=_is_local_relation_cached(name)
                )
                for name in request.names
            }
        else:
            statuses = {
                name: proto_base.ArtifactStatusesResponse.ArtifactStatus(
                    exists=(
                        _is_local_relation_cached(name)
                        or any(name.split("/")[-1] in file for file in files)
                    )
                )
                for name in request.names
            }
        return proto_base.ArtifactStatusesResponse(statuses=statuses)

    def Interrupt(self, request: proto_base.InterruptRequest, context):
        """Interrupts running executions"""
        logger.info("Interrupt")
        telemetry.initialize_request_summary(request)
        # SAS doesn't support operation ids yet (we use a constant SERVER_SIDE_SESSION_ID mock), so
        # instead of using operation ids, we're relying on Snowflake query ids here, meaning that:
        # - The list of returned interrupted_ids contains query ids of interrupted jobs, instead of their operation ids
        # - INTERRUPT_TYPE_OPERATION_ID interrupt type expects a Snowflake query id instead of an operation id
        try:
            match request.interrupt_type:
                case proto_base.InterruptRequest.InterruptType.INTERRUPT_TYPE_ALL:
                    interrupted_ids = interrupt_all_queries()
                case proto_base.InterruptRequest.InterruptType.INTERRUPT_TYPE_TAG:
                    interrupted_ids = interrupt_queries_with_tag(request.operation_tag)
                case proto_base.InterruptRequest.InterruptType.INTERRUPT_TYPE_OPERATION_ID:
                    interrupted_ids = interrupt_query(request.operation_id)
                case _:
                    raise SnowparkConnectNotImplementedError(
                        f"INTERRUPT NOT IMPLEMENTED:\n{request}"
                    )

            return proto_base.InterruptResponse(
                session_id=request.session_id,
                interrupted_ids=interrupted_ids,
            )
        except Exception as e:
            _handle_exception(context, e)
        finally:
            telemetry.send_request_summary_telemetry()

    def ReattachExecute(self, request: proto_base.ReattachExecuteRequest, context):
        """Reattach to an existing reattachable execution.
        The ExecutePlan must have been started with ReattachOptions.reattachable=true.
        If the ExecutePlanResponse stream ends without a ResultComplete message, there is more to
        continue. If there is a ResultComplete, the client should use ReleaseExecute with
        """
        logger.info("ReattachExecute")
        raise SnowparkConnectNotImplementedError(
            "Spark client has detached, please resubmit request. In a future version, the server will be support the reattach."
        )

    def ReleaseExecute(self, request: proto_base.ReleaseExecuteRequest, context):
        """Release an reattachable execution, or parts thereof.
        The ExecutePlan must have been started with ReattachOptions.reattachable=true.
        Non reattachable executions are released automatically and immediately after the ExecutePlan
        RPC and ReleaseExecute may not be used.
        """
        try:
            logger.info("ReleaseExecute")
            return proto_base.ReleaseExecuteResponse(
                session_id=request.session_id,
                operation_id=SERVER_SIDE_SESSION_ID,
            )
        except Exception as e:
            _handle_exception(context, e)

    # TODO: These are required in Spark 4.x.
    # def ReleaseSession(self, request, context):
    #     """Release a session.
    #     All the executions in the session will be released. Any further requests for the session with
    #     that session_id for the given user_id will fail. If the session didn't exist or was already
    #     released, this is a noop.
    #     """
    #     logger.info("ReleaseSession")
    #     return super().ReleaseSession(request, context)
    #
    # def FetchErrorDetails(self, request, context):
    #     """FetchErrorDetails retrieves the matched exception with details based on a provided error id."""
    #     logger.info("FetchErrorDetails")
    #     return super().FetchErrorDetails(request, context)


# Global state related to server connection
_server_running: threading.Event = threading.Event()
_server_error: bool = False
_server_url: Optional[str] = None
_client_url: Optional[str] = None


# Used to reset server global state to the initial blank slate state if error happens during server startup.
# Called after the startup error is caught and handled / logged etc.
def _reset_server_run_state():
    global _server_running, _server_error, _server_url, _client_url
    _server_running.clear()
    _server_error = False
    _server_url = None
    _client_url = None


def _stop_server(stop_event: threading.Event, server: grpc.Server):
    stop_event.wait()
    server.stop(0)
    _reset_server_run_state()
    logger.info("server stop sent")


def _serve(
    stop_event: Optional[threading.Event] = None,
    session: Optional[snowpark.Session] = None,
):
    global _server_running, _server_error
    # TODO: factor out the Snowflake connection code.
    server = None
    try:
        config_snowpark()
        if session is None:
            session = get_or_create_snowpark_session()
        else:
            # If a session is passed in, explicitly call config session to be consistent with sessions created
            # under the hood.
            configure_snowpark_session(session)
        if tcm.TCM_MODE:
            # No need to start grpc server in TCM
            return

        grpc_max_msg_size = get_int_from_env(
            "SNOWFLAKE_GRPC_MAX_MESSAGE_SIZE",
            _SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE,
        )
        grpc_max_metadata_size = get_int_from_env(
            "SNOWFLAKE_GRPC_MAX_METADATA_SIZE",
            _SPARK_CONNECT_GRPC_MAX_METADATA_SIZE,
        )
        server_options = [
            (
                "grpc.max_receive_message_length",
                grpc_max_msg_size,
            ),
            (
                "grpc.max_metadata_size",
                grpc_max_metadata_size,
            ),
            (
                "grpc.absolute_max_metadata_size",
                grpc_max_metadata_size * 2,
            ),
        ]

        from pyspark.sql.connect.client import ChannelBuilder

        ChannelBuilder.MAX_MESSAGE_LENGTH = grpc_max_msg_size

        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10), options=server_options
        )
        control_servicer = ControlServicer(session)
        proto_base_grpc.add_SparkConnectServiceServicer_to_server(
            SnowflakeConnectServicer(control_servicer.log_spark_connect_batch),
            server,
        )
        control_grpc.add_ControlServiceServicer_to_server(control_servicer, server)
        server_url = get_server_url()
        server.add_insecure_port(server_url)
        logger.info(f"Starting Snowpark Connect server on {server_url}...")
        server.start()
        _server_running.set()
        logger.info("Snowpark Connect server started!")
        telemetry.send_server_started_telemetry()
        if stop_event is not None:
            # start a background thread to listen for stop event and terminate the server
            threading.Thread(
                target=_stop_server, args=(stop_event, server), daemon=True
            ).start()
        server.wait_for_termination()
    except Exception as e:
        _server_error = True
        _server_running.set()  # unblock any client sessions
        if "Invalid connection_name 'spark-connect', known ones are " in str(e):
            logger.error(
                "Ensure 'spark-connect' connection config has been set correctly in connections.toml."
            )
        else:
            logger.error("Error starting up Snowpark Connect server", exc_info=True)
        raise e
    finally:
        # flush the telemetry queue if possible
        telemetry.shutdown()


def _set_remote_url(remote_url: str):
    global _server_url, _client_url
    _client_url = remote_url
    parsed_url = urllib.parse.urlparse(remote_url)
    if parsed_url.scheme == "sc":
        _server_url = parsed_url.netloc
        server_port = parsed_url.port or DEFAULT_PORT
        _check_port_is_free(server_port)
    elif parsed_url.scheme == "unix":
        _server_url = remote_url.split("/;")[0]
    else:
        raise RuntimeError(f"Invalid Snowpark Connect URL: {remote_url}")


def _set_server_tcp_port(server_port: int):
    global _server_url, _client_url
    _check_port_is_free(server_port)
    _server_url = f"[::]:{server_port}"
    _client_url = f"sc://127.0.0.1:{server_port}"


def _check_port_is_free(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        if s.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(f"TCP port {port} is already in use")


def _set_server_unix_domain_socket(path: str):
    global _server_url, _client_url
    _server_url = f"unix:{path}"
    _client_url = f"unix:{path}"


def get_server_url() -> str:
    global _server_url
    if not _server_url:
        raise RuntimeError("Server URL not set")
    return _server_url


def get_client_url() -> str:
    global _client_url
    if not _client_url:
        raise RuntimeError("Client URL not set")
    return _client_url


def _make_unix_domain_socket() -> str:
    parent_dir = tempfile.mkdtemp()
    server_path = os.path.join(parent_dir, "snowflake_sas_grpc.sock")
    atexit.register(_cleanup_unix_domain_socket, server_path)
    return server_path


def _cleanup_unix_domain_socket(server_path: str) -> None:
    parent_dir = os.path.dirname(server_path)
    if os.path.exists(server_path):
        os.remove(server_path)
    if os.path.exists(parent_dir):
        os.rmdir(parent_dir)


class UnixDomainSocketChannelBuilder(ChannelBuilder):
    """
    Spark Connect gRPC channel builder for Unix domain sockets
    """

    def __init__(
        self, url: str = None, channelOptions: Optional[List[Tuple[str, Any]]] = None
    ) -> None:
        if url is None:
            url = get_client_url()
        if url[:6] != "unix:/" or len(url) < 7:
            raise PySparkValueError(
                error_class="INVALID_CONNECT_URL",
                message_parameters={
                    "detail": "The URL must start with 'unix://'. Please update the URL to follow the correct format, e.g., 'unix://unix_domain_socket_path'.",
                },
            )

        # Rewrite the URL to use http as the scheme so that we can leverage
        # Python's built-in parser to parse URL parameters
        fake_url = "http://" + url[6:]
        self.url = urllib.parse.urlparse(fake_url)
        self.params: Dict[str, str] = {}
        self._extract_attributes()

        # Now parse the real unix domain socket URL
        self.url = urllib.parse.urlparse(url)

        GRPC_DEFAULT_OPTIONS = [
            ("grpc.max_send_message_length", _SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE),
            ("grpc.max_receive_message_length", _SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE),
            ("grpc.max_metadata_size", _SPARK_CONNECT_GRPC_MAX_METADATA_SIZE),
            (
                "grpc.absolute_max_metadata_size",
                2 * _SPARK_CONNECT_GRPC_MAX_METADATA_SIZE,
            ),
        ]

        if channelOptions is None:
            self._channel_options = GRPC_DEFAULT_OPTIONS
        else:
            self._channel_options = GRPC_DEFAULT_OPTIONS + channelOptions
        # For Spark 4.0 support, but also backwards compatible.
        self._params = self.params

    def _extract_attributes(self) -> None:
        """Extract attributes from parameters.

        This method was copied from
        https://github.com/apache/spark/blob/branch-3.5/python/pyspark/sql/connect/client/core.py

        This is required for Spark 4.0 support, since it is dropped in favor of moving
        the extraction logic into the constructor.
        """
        if len(self.url.params) > 0:
            parts = self.url.params.split(";")
            for p in parts:
                kv = p.split("=")
                if len(kv) != 2:
                    raise PySparkValueError(
                        error_class="INVALID_CONNECT_URL",
                        message_parameters={
                            "detail": f"Parameter '{p}' should be provided as a "
                            f"key-value pair separated by an equal sign (=). Please update "
                            f"the parameter to follow the correct format, e.g., 'key=value'.",
                        },
                    )
                self.params[kv[0]] = urllib.parse.unquote(kv[1])

        netloc = self.url.netloc.split(":")
        if len(netloc) == 1:
            self.host = netloc[0]
            if version.parse(pyspark.__version__) >= version.parse("4.0.0"):
                from pyspark.sql.connect.client.core import DefaultChannelBuilder

                self.port = DefaultChannelBuilder.default_port()
            else:
                self.port = ChannelBuilder.default_port()
        elif len(netloc) == 2:
            self.host = netloc[0]
            self.port = int(netloc[1])
        else:
            raise PySparkValueError(
                error_class="INVALID_CONNECT_URL",
                message_parameters={
                    "detail": f"Target destination '{self.url.netloc}' should match the "
                    f"'<host>:<port>' pattern. Please update the destination to follow "
                    f"the correct format, e.g., 'hostname:port'.",
                },
            )

    # We override this to enable compatibility with Spark 4.0
    host = None

    @property
    def endpoint(self) -> str:
        return f"{self.url.scheme}:{self.url.path}"

    def toChannel(self) -> grpc.Channel:
        return grpc.insecure_channel(self.endpoint, options=self._channel_options)


def config_snowpark() -> None:
    """
    Some snowpark configs required by SAS.
    """

    # Enable structType. Require snowpark 1.27.0 or snowpark main branch after commit 888cec55c4
    import snowflake.snowpark.context as context

    context._use_structured_type_semantics = True
    context._is_snowpark_connect_compatible_mode = True


def start_jvm():
    # The JVM is used to run the Spark parser and JDBC drivers,
    # so needs to be configured to support both.

    # JDBC driver .jars are added using the CLASSPATH env var.
    # We then add the Spark parser jars (that are shipped with pyspark)
    # by appending them to the default classpath.

    # Since we need to control JVM's parameters, fail immediately
    # if the JVM has already been started elsewhere.
    if jpype.isJVMStarted():
        if tcm.TCM_MODE:
            # No-op if JVM is already started in TCM mode
            return
        raise RuntimeError(
            "JVM must not be running when starting the Spark Connect server"
        )

    pyspark_jars = (
        pathlib.Path(snowflake.snowpark_connect.__file__).parent / "includes/jars"
    )

    if "dataframe_processor.zip" in str(pyspark_jars):
        # importlib.resource doesn't work when local stage package is used in TCM
        zip_path = pathlib.Path(
            snowflake.snowpark_connect.__file__
        ).parent.parent.parent
        temp_dir = tempfile.gettempdir()

        extract_folder = "snowflake/snowpark_connect/includes/jars/"  # Folder to extract (must end with '/')

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for member in zip_ref.namelist():
                if member.startswith(extract_folder):
                    zip_ref.extract(member, path=temp_dir)

        pyspark_jars = pathlib.Path(temp_dir) / extract_folder

    for path in pyspark_jars.glob("**/*.jar"):
        jpype.addClassPath(path)

    # TODO: Should remove convertStrings, but it breaks the JDBC code.
    jvm_settings: list[str] = list(
        filter(
            lambda e: e != "",
            os.environ.get("JAVA_OPTS", "").split(),
        )
    )
    # Add JVM memory constraints to reduce memory usage
    jpype.startJVM(
        *jvm_settings,
        convertStrings=True,
    )


def start_session(
    is_daemon: bool = True,
    remote_url: Optional[str] = None,
    tcp_port: Optional[int] = None,
    unix_domain_socket: Optional[str] = None,
    stop_event: threading.Event = None,
    snowpark_session: Optional[snowpark.Session] = None,
    connection_parameters: Optional[Dict[str, str]] = None,
    max_grpc_message_size: int = _SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE,
) -> threading.Thread | None:
    """
    Starts Spark Connect server connected to Snowflake. No-op if the Server is already running.

    Parameters:
        is_daemon (bool): Should run the server as daemon or not. use True to automatically shut the Spark connect
                          server down when the main program (or test) finishes. use False to start the server in a
                          stand-alone, long-running mode.
        remote_url (Optional[str]): sc:// URL on which to start the Spark Connect server. This option is incompatible with the tcp_port
                                    and unix_domain_socket parameters.
        tcp_port (Optional[int]): TCP port on which to start the Spark Connect server. This option is incompatible with
                                  the remote_url and unix_domain_socket parameters.
        unix_domain_socket (Optional[str]): Path to the unix domain socket on which to start the Spark Connect server.
                                            This option is incompatible with the remote_url and tcp_port parameters.
        stop_event (Optional[threading.Event]): Stop the SAS server when stop_event.set() is called.
                                                Only works when is_daemon=True.
        snowpark_session: A Snowpark session to use for this connection; currently the only applicable use of this is to
                          pass in the session created by the stored proc environment.
        connection_parameters: A dictionary of connection parameters to use to create the Snowpark session. If this is
                                provided, the `snowpark_session` parameter must be None.
    """
    try:
        # Changing the value of our global variable based on the grpc message size provided by the user.
        global _SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE
        _SPARK_CONNECT_GRPC_MAX_MESSAGE_SIZE = max_grpc_message_size

        if os.environ.get("SPARK_ENV_LOADED"):
            raise RuntimeError(
                "Snowpark Connect cannot be run inside of a Spark environment"
            )
        if connection_parameters is not None:
            if snowpark_session is not None:
                raise ValueError(
                    "Only specify one of snowpark_session and connection_parameters"
                )
            snowpark_session = snowpark.Session.builder.configs(
                connection_parameters
            ).create()

        global _server_running, _server_error
        if _server_running.is_set():
            url = get_client_url()
            logger.warning(f"Snowpark Connect session is already running at {url}")
            return

        if len(list(filter(None, [remote_url, tcp_port, unix_domain_socket]))) > 1:
            raise RuntimeError(
                "Can only set at most one of remote_url, tcp_port, and unix_domain_socket"
            )

        url_from_env = os.environ.get("SPARK_REMOTE", None)
        if remote_url:
            _set_remote_url(remote_url)
        elif tcp_port:
            _set_server_tcp_port(tcp_port)
        elif unix_domain_socket:
            _set_server_unix_domain_socket(unix_domain_socket)
        elif url_from_env:
            # Spark clients use environment variable SPARK_REMOTE to figure out Spark Connect URL. If none of the
            # connection properties (remote_url, tcp_port, unix_domain_socket) are explicitly passed in to this
            # function then we should try and mimic clients' behavior
            # i.e. read the server URL from the SPARK_REMOTE environment variable.
            _set_remote_url(url_from_env)
        else:
            # No connection properties can be found at all - either as arguments to this function or int the environment
            # variable. We use random, unique Unix Domain Socket as a last fallback. Client can connect to this randomly
            # generated UDS port using snowpark_connect.get_session().
            # Mostly used in stored procs and Notebooks to avoid port conflicts.
            if os.name == "nt":
                # Windows does not support unix domain sockets, so use default TCP port instead.
                _set_server_tcp_port(DEFAULT_PORT)
            else:
                # Generate unique, random UDS port. Mostly useful in stored proc environment to avoid port conflicts.
                unix_domain_socket = _make_unix_domain_socket()
                _set_server_unix_domain_socket(unix_domain_socket)

        start_jvm()
        _disable_protobuf_recursion_limit()

        if is_daemon:
            arguments = (stop_event, snowpark_session)
            # `daemon=True` ensures the server thread exits when script finishes.
            server_thread = threading.Thread(target=_serve, args=arguments, daemon=True)
            server_thread.start()
            _server_running.wait()
            if _server_error:
                raise RuntimeError("Snowpark Connect session failed to start")
            return server_thread
        else:
            # Launch in the foreground.
            _serve(session=snowpark_session)
    except Exception as e:
        _reset_server_run_state()
        logger.error(e, exc_info=True)
        raise e


def get_session(url: Optional[str] = None, conf: SparkConf = None) -> SparkSession:
    """
    Returns spark connect session

    Parameters:
        url (Optional[str]): Spark connect server URL. Uses default server URL if none is provided.

    Returns:
        A new spark connect session

    Raises:
        RuntimeError: If Spark Connect server is not started.
    """
    try:
        if not url:
            url = get_client_url()

        if url.startswith("unix:/"):
            b = SparkSession.builder.channelBuilder(UnixDomainSocketChannelBuilder())
        else:
            b = SparkSession.builder.remote(url)

        if conf is not None:
            for k, v in conf.getAll():
                b.config(k, v)

        return b.getOrCreate()
    except Exception as e:
        _reset_server_run_state()
        logger.error(e, exc_info=True)
        raise e


def init_spark_session(conf: SparkConf = None) -> SparkSession:
    if os.environ.get("JAVA_HOME") is None:
        try:
            # For Notebooks on SPCS
            from jdk4py import JAVA_HOME

            os.environ["JAVA_HOME"] = str(JAVA_HOME)
        except ModuleNotFoundError:
            # For notebooks on Warehouse
            conda_prefix = os.environ.get("CONDA_PREFIX")
            if conda_prefix is not None:
                os.environ["JAVA_HOME"] = conda_prefix
                os.environ["JAVA_LD_LIBRARY_PATH"] = os.path.join(
                    conda_prefix, "lib", "server"
                )
    logger.info("JAVA_HOME=%s", os.environ.get("JAVA_HOME", "Not defined"))

    os.environ["SPARK_LOCAL_HOSTNAME"] = "127.0.0.1"
    os.environ["SPARK_CONNECT_MODE_ENABLED"] = "1"

    from snowflake.snowpark_connect.utils.session import _get_current_snowpark_session

    snowpark_session = _get_current_snowpark_session()
    start_session(snowpark_session=snowpark_session)
    return get_session(conf=conf)


def enable_debug_logging():
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)


def _get_files_metadata(data_source: relations_proto.Read.DataSource) -> List[str]:
    # TODO: Handle paths on the cloud
    paths = data_source.paths
    extension = data_source.format if data_source.format != "text" else "txt"
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(f"file://{path}")
        else:
            files.extend(
                [
                    f"file://{path}/{f}"
                    for f in os.listdir(path)
                    if f.endswith(extension)
                ]
            )
    return files


def _disable_protobuf_recursion_limit():
    # https://github.com/protocolbuffers/protobuf/blob/960e79087b332583c80537c949621108a85aa442/src/google/protobuf/io/coded_stream.h#L616
    # Disable protobuf recursion limit (default 100) because Spark workloads often produce deeply nested execution plans. For example:
    # - Queries with many unions
    # - Complex expressions with multiple levels of nesting
    # Without this, legitimate Spark queries would fail with `(DecodeError) Error parsing message with type 'spark.connect.Relation'` error.
    # see test_sql_resulting_in_nested_protobuf
    from google.protobuf.pyext import cpp_message

    cpp_message._message.SetAllowOversizeProtos(True)
