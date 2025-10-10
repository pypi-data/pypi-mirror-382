#!/usr/bin/env python3
#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import argparse
import logging

if __name__ == "__main__":
    from snowflake.snowpark_connect.server import start_session

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--tcp-port", type=int)
    group.add_argument("--unix-domain-socket", type=str)
    group.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    unix_domain_socket = args.unix_domain_socket
    tcp_port = args.tcp_port
    if not unix_domain_socket and not tcp_port:
        tcp_port = 15002  # default spark connect server port

    if args.verbose:
        logger = logging.getLogger("snowflake_connect_server")
        logger.setLevel(logging.INFO)

    start_session(
        is_daemon=False,
        tcp_port=tcp_port,
        unix_domain_socket=unix_domain_socket,
    )
