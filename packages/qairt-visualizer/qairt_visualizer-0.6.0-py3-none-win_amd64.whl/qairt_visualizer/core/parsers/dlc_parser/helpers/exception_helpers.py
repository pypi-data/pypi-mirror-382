# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""CLI Exception Helpers"""

import json
import sys


def handle_exception(e: Exception):
    """
    Handles CLI script exceptions
    :param e: The exception to be serialized to JSON
    """
    error = {"errorType": type(e).__name__, "message": str(e)}
    print(json.dumps(error), file=sys.stderr)
