#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import os
import subprocess

from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Starting Datatailr excel add-in...")

    entrypoint = os.environ.get("DATATAILR_ENTRYPOINT")
    if entrypoint is None:
        raise ValueError("Environment variable 'DATATAILR_ENTRYPOINT' is not set.")

    local = os.environ.get("DATATAILR_LOCAL", False) in ("1", "true", "True", "TRUE")
    if local:
        hostname = "localhost.excel.datatailr.com"
        local_flag = "-l"
    else:
        hostname = os.environ.get("DATATAILR_HOST")
        if hostname is None:
            raise ValueError("Environment variable 'DATATAILR_HOST' is not set.")
        local_flag = ""

    module_name = entrypoint.split(":", 1)[0]

    entrypoint = f'/opt/datatailr/bin/dt-excel.sh -n -H "{hostname}" {local_flag} -p 8080 -w 8000 {module_name}'
    logger.info(f"Running entrypoint: {entrypoint}")
    subprocess.run(entrypoint, shell=True)
