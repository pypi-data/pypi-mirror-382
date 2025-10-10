# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""UI helper functions"""

import os
from importlib.resources import files

from qairt_visualizer.helpers.string_helpers import is_none_or_empty


def find_ui_path_to(target: str, ui_module: str = "qairt_visualizer.core.ui") -> str:
    """
    Returns the path to target file under the ui folder
    :param target_file: Full filename
    :return: Absolute path to the target_file
    """
    if is_none_or_empty(target):
        raise ValueError("UI target cannot be None. Cannot open Visualizer.")
    target_path = str(files(ui_module).joinpath(target.strip()))
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Unable to locate {target} under {target_path}. Cannot open Visualizer.")
    return target_path
