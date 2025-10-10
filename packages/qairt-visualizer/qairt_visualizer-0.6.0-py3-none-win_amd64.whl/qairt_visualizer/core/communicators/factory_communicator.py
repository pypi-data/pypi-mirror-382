# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Communicator Factory Functions"""

from qairt_visualizer.core.communicators.base_communicator_context import BaseCommunicatorContext
from qairt_visualizer.core.communicators.electron_communicator_context import ElectronCommunicatorContext
from qairt_visualizer.core.communicators.web_communicator_context import WebCommunicatorContext
from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.models.app_environment_enum import AppEnvironment


def get_communicator(communicator_type: AppEnvironment) -> BaseCommunicatorContext:
    """
    Returns an instance of Communicator
    """
    match communicator_type:
        case AppEnvironment.WEB:
            return WebCommunicatorContext()
        case AppEnvironment.ELECTRON:
            return ElectronCommunicatorContext()
        case _:
            message = f"Invalid communication type: {communicator_type}. Cannot communicate to Visualizer."
            api_logger.critical(message)
            raise ValueError(message)
