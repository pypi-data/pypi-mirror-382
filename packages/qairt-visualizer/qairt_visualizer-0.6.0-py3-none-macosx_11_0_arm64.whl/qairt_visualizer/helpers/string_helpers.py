# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""String helper functions"""

from typing import Any


def is_none_or_empty(variable: Any) -> bool:
    """
    Verifies if a given variable is None, an empty string, any empty string or None exists in a list,
    or an empty list

    :param variable: The object to be verified
    """
    if variable is None:
        return True
    if isinstance(variable, str) and not variable.strip():
        return True
    if isinstance(variable, list) and (not variable or any(map(is_none_or_empty, variable))):
        return True
    return False
