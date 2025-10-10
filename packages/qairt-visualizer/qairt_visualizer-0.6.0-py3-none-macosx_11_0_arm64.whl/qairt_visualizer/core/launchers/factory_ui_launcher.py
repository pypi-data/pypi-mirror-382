# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""UI Launcher Factory Functions"""

from qairt_visualizer.core.launchers.base_ui_launcher_context import BaseUILauncherContext
from qairt_visualizer.core.launchers.electron_launcher_context import ElectronLauncherContext
from qairt_visualizer.core.launchers.web_launcher_context import WebLauncherContext
from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.models.app_environment_enum import AppEnvironment


def get_launcher(launcher_type: AppEnvironment) -> BaseUILauncherContext:
    """
    Returns an instance of the UI Launcher
    """
    match launcher_type:
        case AppEnvironment.WEB:
            return WebLauncherContext()
        case AppEnvironment.ELECTRON:
            return ElectronLauncherContext()
        case _:
            message = f"Invalid application type: {launcher_type}. Cannot open Visualizer."
            api_logger.critical(message)
            raise ValueError(message)
