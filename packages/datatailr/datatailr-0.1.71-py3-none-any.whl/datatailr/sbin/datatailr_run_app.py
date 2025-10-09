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
import sys
import runpy
import inspect
import importlib

from datatailr.logging import DatatailrLogger


logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Starting Datatailr app...")
    entrypoint = os.environ.get("DATATAILR_ENTRYPOINT")
    if entrypoint is None or ":" not in entrypoint:
        raise ValueError(
            "Environment variable 'DATATAILR_ENTRYPOINT' is not in the format 'module_name:file_name'."
        )

    module_name, func_name = entrypoint.split(":")

    # consider using ast
    module = importlib.import_module(module_name)
    function = getattr(module, func_name)
    script = inspect.getfile(function)
    sys.argv = [
        "streamlit",
        "run",
        str(script),
        "--server.address",
        "0.0.0.0",
        "--server.port",
        "8080",
        "--server.headless",
        "true",
        *sys.argv[1:],
    ]
    logger.info(f"Running entrypoint: {entrypoint}")
    runpy.run_module("streamlit", run_name="__main__")
