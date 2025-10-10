# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Visualizer Service"""

import os
from pathlib import Path
from typing import List, Optional, Union

from qairt_visualizer.core.communicators.base_communicator_context import BaseCommunicatorContext
from qairt_visualizer.core.launchers.base_ui_launcher_context import BaseUILauncherContext
from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.helpers.string_helpers import is_none_or_empty
from qairt_visualizer.models.display_options import DisplayOptions
from qairt_visualizer.schemas.view_schemas import ViewRequest


class VisualizerService:
    """
    Service class used to orchestrate interactions between the UI launcher and communicator classes
    """

    def __init__(self, ui_launcher: BaseUILauncherContext, communicator: BaseCommunicatorContext):
        self._ui_launcher = ui_launcher
        self._communicator = communicator
        self._path_to_model: Optional[str] = None
        self._report_list: Optional[List[str]] = None
        self._visualizer_opened = False

    async def view(
        self,
        path_to_model: Optional[str] = None,
        reports: Optional[Union[str, List[str]]] = None,
        options: DisplayOptions = DisplayOptions(),
    ):
        """
        Opens a visualization window to display a model, reports, or both. If a model path is given, all
        reports must be related to that model and must have a unique type code (e.g., mutliple optrace
        reports would result in an error). If no model is passed in, reports may refer to different models
        and do not need unique type codes.

        :param path_to_model: Optional path to a given model
        :param reports: A single path or list of paths representing different reports for the
        visualization window to display.
        """

        model_path_empty = is_none_or_empty(path_to_model)
        report_paths_empty = is_none_or_empty(reports)

        if model_path_empty and report_paths_empty:
            raise ValueError(
                "Invalid input: Both 'path_to_model' and 'reports' cannot be None. "
                "Please provide a value for at least one of these parameters."
            )

        if not model_path_empty:
            self._path_to_model = str(Path(os.path.expanduser(path_to_model)).absolute())  # type: ignore
            if not os.path.exists(self._path_to_model):
                raise FileNotFoundError(f"{self._path_to_model} cannot be located")

        if not report_paths_empty:
            report_paths = reports if isinstance(reports, list) else [reports]  # type: ignore
            self._report_list = [
                str(Path(os.path.expanduser(report_path)).absolute()) for report_path in report_paths
            ]

            invalid_paths = [
                report_path for report_path in self._report_list if not os.path.exists(report_path)
            ]
            if len(invalid_paths) > 0:
                paths = "\n".join(invalid_paths)
                raise FileNotFoundError(f"The following paths cannot be located: {paths}")

        api_logger.debug("Searching for existing Visualizer UI process...")
        existing_process_port = self._ui_launcher.find_ui_process_port()

        if existing_process_port == -1:
            api_logger.debug("No existing Visualizer UI process found. Attempting to launch new one.")
            port = self._ui_launcher.launch()
            self._communicator.port = port
        else:
            api_logger.debug("Found existing Visualizer UI process.")
            self._communicator.port = existing_process_port

        api_logger.debug("Visualizer UI port: %s", self._communicator.port)

        await self._ui_launcher.after_launch_tasks(self._communicator.port)

        api_logger.info("Sending view request to Visualizer UI.")
        api_logger.info("Using options %s", options)
        await self._communicator.send(
            ViewRequest(
                path_to_model=self._path_to_model,
                reports=self._report_list,
                id=self._ui_launcher.id,
                options=options,
            )
        )
