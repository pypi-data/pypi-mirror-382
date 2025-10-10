# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""AppEnvironment enums"""

from enum import Enum


class AppEnvironment(Enum):
    """
    Enums representing the different modes of how the visualizer UI will be served
    """

    WEB = "web"
    ELECTRON = "electron"
