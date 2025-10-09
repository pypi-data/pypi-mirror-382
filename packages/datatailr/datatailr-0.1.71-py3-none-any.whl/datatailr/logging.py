# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from datatailr import User
from datatailr.wrapper import dt__Tag


def get_log_level() -> int:
    log_level = os.getenv("DATATAILR_LOG_LEVEL", "INFO").upper()
    if log_level in ["TRACE", "DEBUG"]:
        return logging.DEBUG
    elif log_level == "INFO":
        return logging.INFO
    elif log_level == "WARNING":
        return logging.WARNING
    elif log_level == "ERROR":
        return logging.ERROR
    elif log_level == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO


class MaxLevelFilter(logging.Filter):
    """Allow only log records at or below a given level."""

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.level


class MinLevelFilter(logging.Filter):
    """Allow only log records at or above a given level."""

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.level


tag = dt__Tag()
node_name = tag.get("node_name") or "local"
node_ip = tag.get("node_ip")
job_name = os.getenv("DATATAILR_JOB_NAME", "unknown_job")

try:
    user = User.signed_user().name
except Exception:
    import getpass

    user = getpass.getuser()

LOG_FORMAT = f"%(asctime)s - %(levelname)s - {node_name}:{node_ip} - {user} - {job_name} - %(name)s - [Line %(lineno)d]: %(message)s"


class DatatailrLogger:
    def __init__(
        self,
        name: str,
        log_file: Optional[str] = None,
        log_level: int = get_log_level(),
        log_format: str = LOG_FORMAT,
    ):
        """
        Initialize the DatatailrLogger.

        :param name: Name of the logger.
        :param log_file: Optional file to log messages to.
        :param log_level: Logging level (default: logging.INFO).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        formatter = logging.Formatter(log_format)

        # stdout handler (DEBUG/INFO only)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(MaxLevelFilter(logging.INFO))
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

        # stderr handler (WARNING and above)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.addFilter(MinLevelFilter(logging.WARNING))
        stderr_handler.setFormatter(formatter)
        self.logger.addHandler(stderr_handler)

        # Optional file handler
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.enable_opentelemetry()

    def get_logger(self):
        """
        Get the configured logger instance.

        :return: Configured logger.
        """
        return self.logger

    def enable_opentelemetry(self):
        """
        Enable OpenTelemetry integration if available.
        """
        try:
            from opentelemetry.instrumentation.logging import LoggingInstrumentor  # type: ignore

            LoggingInstrumentor().instrument(set_logging_format=True)
        except ImportError:
            pass  # OpenTelemetry is not installed, skip instrumentation
