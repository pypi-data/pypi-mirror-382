# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""QAIRT Python API helper functions"""

import tempfile
from typing import Any, List, Optional, Tuple, Union

from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger


def save_qairt_object(qairt_object: Any) -> str:
    """

    Saves the input QAIRT Model object to disk

    :param qairt_object: QAIRT Model object to save to disk
    :return: str - The path to the newly saved model or report
    """

    suffix = ".dlc" if qairt_object.__class__.__name__ == "Model" else ".json"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        api_logger.info("Temporary file created at:  %s", temp_file.name)
        qairt_object.save(temp_file.name)
        return temp_file.name


def process_model_and_reports(
    model: Optional[Union[str, Any]] = None,
    reports: Optional[Union[str, List[str]]] = None,
) -> Tuple[Optional[str], Optional[Union[str, List[str]]]]:
    """
    Checks the input model or reports and, if they are QAIRT objects,
    saves the input QAIRT Model object to disk

    :param model: Model path or QAIRT Model object
    :param reports: A single path or list of paths representing different reports for the
        visualization window to display.
    :return: Tuple[Optional[str], Optional[Union[str, List[str]]]] - The path to the model to be
        visualized and/or the list report paths to be visualized
    """
    if model and not isinstance(model, str):
        model = save_qairt_object(model)
    # AISW-131213
    # if reports:
    #     if isinstance(reports, ProfilingReport):
    #         reports = save_qairt_object(reports)
    #     elif isinstance(reports, list):
    #         reports = [
    #             save_qairt_object(report) if isinstance(report, ProfilingReport) else report
    #             for report in reports
    #         ]

    return model, reports
