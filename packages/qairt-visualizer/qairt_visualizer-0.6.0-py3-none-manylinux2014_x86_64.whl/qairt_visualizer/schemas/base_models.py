# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Visualizer Base Models"""

from pydantic import BaseModel, ConfigDict


class VisualizerBaseModel(BaseModel):
    """
    Visualizer-specific BaseModel class
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
