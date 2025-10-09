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
import importlib

from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Starting Datatailr service...")
    entrypoint = os.environ.get("DATATAILR_ENTRYPOINT")
    port = os.environ.get("DATATAILR_SERVICE_PORT")

    if entrypoint is None:
        raise ValueError("Environment variable 'DATATAILR_ENTRYPOINT' is not set.")

    if port is None:
        raise ValueError("Environment variable 'DATATAILR_SERVICE_PORT' is not set.")

    module_name, func_name = entrypoint.split(":")

    entrypoint_module = importlib.import_module(module_name)
    logger.info(f"Running entrypoint: {entrypoint}")
    getattr(entrypoint_module, func_name)(int(port))
