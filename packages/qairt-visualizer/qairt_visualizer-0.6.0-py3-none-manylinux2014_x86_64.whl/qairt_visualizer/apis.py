# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""APIs"""

import asyncio
import platform
from typing import List, Optional, Union

from qairt_visualizer.core.communicators.base_communicator_context import BaseCommunicatorContext
from qairt_visualizer.core.communicators.factory_communicator import get_communicator
from qairt_visualizer.core.launchers.base_ui_launcher_context import BaseUILauncherContext
from qairt_visualizer.core.launchers.factory_ui_launcher import get_launcher
from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.core.visualizer_logging.logging_config import LoggingConfig
from qairt_visualizer.core.visualizer_service import VisualizerService
from qairt_visualizer.helpers.asyncio_helpers import has_event_loop_running
from qairt_visualizer.helpers.jupyter_helpers import is_running_in_jupyter
from qairt_visualizer.helpers.qairt_helpers import process_model_and_reports
from qairt_visualizer.models.app_environment_enum import AppEnvironment
from qairt_visualizer.models.display_options import DisplayOptions
from qairt_visualizer.models.validators.model_validator import validate_model
from qairt_visualizer.models.validators.validate_args import validate_args


@validate_args(
    {
        "model": validate_model,
    }
)
def view(
    model: Optional[Union[str, object]] = None,
    reports: Optional[Union[str, List[str]]] = None,
    options: Optional[DisplayOptions] = None,
):
    """
    Opens a visualization window(s) to display a model, reports, or both.

    :param model: Optional path to a given model or QAIRT Model object
    :param reports: A single path or list of paths representing different reports for the
        visualization window to display.
    :param options: Customizes the visualization window behavior.
    """
    LoggingConfig.setup_logging()

    options = options or DisplayOptions()

    if platform.system().lower() == "windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore

    # Interactive environments like jupyter and IPython automatically run a loop in the background.
    # Because asyncio.run cannot be called when a loop is already running,
    # we check if one is already running and use asyncio.gather instead.
    mode = AppEnvironment.WEB if is_running_in_jupyter() else AppEnvironment.ELECTRON
    api_logger.debug("View mode: %s", mode)

    launcher = get_launcher(mode)
    communicator = get_communicator(mode)

    path_to_processed_model, path_to_processed_reports = process_model_and_reports(model, reports)

    if has_event_loop_running():
        loop = asyncio.get_running_loop()
        t = loop.create_task(
            _view(launcher, communicator, path_to_processed_model, path_to_processed_reports, options)
        )
        asyncio.gather(t)
    else:
        asyncio.run(
            _view(launcher, communicator, path_to_processed_model, path_to_processed_reports, options)
        )


async def _view(
    launcher: BaseUILauncherContext,
    communicator: BaseCommunicatorContext,
    path_to_model: Optional[str] = None,
    reports: Optional[Union[str, List[str]]] = None,
    options: DisplayOptions = DisplayOptions(),
):
    """
    Opens a visualization window to display a model, reports, or both based on the input launcher type

    :param launcher: The mechanism used to display the visualization window (either Jupyter or Electron)
    :param communicator: The communicator used to communicate between the Python API and the visualization
    :param path_to_model: Optional path to a given model
    :param reports: A single path or list of paths representing different reports for the
        visualization window to display.
    :param options: Customizes the visualization window behavior.
    """
    api_logger.info("Intializing visualizer service")

    visualizer = VisualizerService(launcher, communicator)
    try:
        await visualizer.view(path_to_model=path_to_model, reports=reports, options=options)
    except Exception as e:  # pylint: disable=broad-exception-caught
        api_logger.debug(e, exc_info=True)
        api_logger.error("An error occurred when attempting to view: %s", str(e))
