# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Jupyer helper functions"""

from IPython.core.getipython import get_ipython


def is_running_in_jupyter() -> bool:
    """
    Returns True if running in jupyter, false if otherwise
    """
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    except Exception:  # pylint: disable=broad-exception-caught
        return False
