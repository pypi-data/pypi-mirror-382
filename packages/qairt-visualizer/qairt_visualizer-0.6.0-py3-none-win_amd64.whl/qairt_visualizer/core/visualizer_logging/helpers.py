# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Logger helpers"""

import logging
import logging.handlers
from typing import Union

from qairt_visualizer.core.visualizer_logging.logger_constants import API_LOGGER
from qairt_visualizer.core.visualizer_logging.logging_config import LoggingConfig


def set_log_level(level: Union[str, int]):
    """Sets the log level for the API's console logger only

    :param level: The desired log level
    :raises ValueError: Level was not recognized
    """
    if not _is_valid_logging_level(level):
        raise ValueError(f"{level} is not a valid logging level.")

    LoggingConfig.setup_logging()
    api_logger = logging.getLogger(API_LOGGER)
    level = level.upper() if isinstance(level, str) else logging.getLevelName(level)

    console_handler = next(
        (handler for handler in api_logger.handlers if handler.get_name() == "console"), None
    )
    if not console_handler:
        raise RuntimeError("No console log handler found.")
    console_handler.setLevel(level)


def _is_valid_logging_level(level: Union[str, int]):
    if isinstance(level, str):
        return level.upper() in {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

    return level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
