# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Contains schemas for related to the view API"""

from typing import List, Literal, Optional

from pydantic import model_validator
from typing_extensions import Self

from qairt_visualizer.models.display_options import DisplayOptions
from qairt_visualizer.schemas.base_models import VisualizerBaseModel


class ViewRequest(VisualizerBaseModel):
    """
    Model representing a request to view a model and/or associated reports.

    :param id: Custom ID used to identify the visualize window that will be displaying the request
    :param path_to_model: The absolute file path to a model.
    :param reports: A list of JSON strings, where each JSON string represents a single report.
    :param options: Customizes the visualization window behavior.
    """

    id: Optional[str]
    path_to_model: Optional[str]
    reports: Optional[List[str]]
    options: DisplayOptions = DisplayOptions()

    @model_validator(mode="after")
    def check_model_reports(self) -> Self:
        """Validates object such that path_to_model and reports both cannot be None

        :param values: values from instance
        """
        if self.path_to_model is None and (self.reports is None or len(self.reports) == 0):
            raise ValueError("Either path_to_model or reports must be provided.")
        return self


class ViewResponse(VisualizerBaseModel):
    """
    Model representing a response to a given ViewRequest.

    :param status: Indicates whether the view operation was successful or encountered an error.
    :param message: A descriptive message providing additional information about the status of the view
                    operation. This could include error details if the status is "error" or a
                    success confirmation if the status is "success".
    :param request_payload: The ViewRequest object that this response is associated with,
                    containing the original request details.
    """

    status: Literal["success", "error"]
    message: str
    request_payload: ViewRequest
