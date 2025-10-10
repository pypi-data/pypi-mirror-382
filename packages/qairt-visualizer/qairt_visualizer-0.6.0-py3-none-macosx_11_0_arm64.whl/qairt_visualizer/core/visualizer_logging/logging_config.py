# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Logging config model"""

import logging
import os
import threading
from logging import config
from typing import Dict

from qairt_visualizer.core.visualizer_logging.logger_constants import (
    API_LOGGER,
    WEB_SERVER_LOGGER,
)


class LoggingConfig:
    """Logging config"""

    _lock = threading.Lock()
    _configured = False

    @classmethod
    def setup_logging(cls) -> None:
        """
        Sets logging configuration and ensures it's not configured multiple times
        """
        with cls._lock:
            if cls._configured:
                return
            config.dictConfig(LoggingConfig.get_py_logging_config())
            cls._configured = True

    @staticmethod
    def get_py_logging_config() -> Dict:
        """
        Returns the Python logging configuration dictionary
        """
        # Create the logging directory
        try:
            log_dir = os.environ.get(
                "QAIRT_VISUALIZER_LOG_DIRECTORY", os.path.expanduser("~/.qairt_visualizer/logs")
            )
            os.makedirs(log_dir, exist_ok=True)
        except OSError:
            logging.exception("Failed to initialize logging directory %s", log_dir)
            raise

        file_handler_common_settings: Dict = {
            "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
            "formatter": "extended",
            "level": "INFO",
            "when": "midnight",  # Rotate at midnight
            "interval": 7,  # Rotate every day
            "backupCount": 3,  # Keep only 3 day's worth of logs
        }
        return {
            "version": 1,
            "formatters": {
                "simple": {"format": "%(name)s: %(asctime)s | %(levelname)s | %(message)s"},
                "extended": {
                    "format": "%(name)s: %(asctime)s | %(levelname)s | %(funcName)s | "
                    "%(filename)s:%(lineno)s - %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%SZ",
                },
                "debug": {
                    "format": "%(name)s: %(asctime)s | %(levelname)s | "
                    "%(filename)s:%(lineno)s - %(message)s | %(threadName)s | %(process)d",
                    "datefmt": "%Y-%m-%dT%H:%M:%SZ",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "simple",
                },
                "api_file_handler": {
                    **file_handler_common_settings,
                    "filename": f"{os.path.join(log_dir, 'visualizer-api.log')}",
                    "level": "DEBUG",
                },
                "web_server_file_handler": {
                    **file_handler_common_settings,
                    "filename": f"{os.path.join(log_dir, 'visualizer-web-server.log')}",
                    "level": "DEBUG",
                },
            },
            "loggers": {
                f"{API_LOGGER}": {
                    "level": "DEBUG",
                    "handlers": ["api_file_handler", "console"],
                    "propagate": False,
                },
                f"{WEB_SERVER_LOGGER}": {
                    "level": "DEBUG",
                    "handlers": ["web_server_file_handler"],
                },
                "uvicorn.error": {
                    "handlers": ["web_server_file_handler"],
                    "level": "INFO",
                },
                "uvicorn.access": {
                    "handlers": ["web_server_file_handler"],
                    "level": "INFO",
                },
            },
        }
