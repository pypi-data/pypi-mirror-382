# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Asyncio helper functions"""

import asyncio


def has_event_loop_running() -> bool:
    """
    Returns True if an event loop is already running, False if otherwise
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False
