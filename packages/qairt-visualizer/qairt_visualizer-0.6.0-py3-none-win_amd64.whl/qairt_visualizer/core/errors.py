# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Custom error classes"""

from typing import Optional


class ReceiveError(Exception):
    """Custom error class used when there is an issue receiving a message"""

    def __init__(self, message: str, response: str):
        super().__init__(message)
        self.response = response

    def __str__(self):
        return f"{self.args[0]}, Response: {self.response}"


class HttpError(Exception):
    """Custom error class used for http exceptions"""

    def __init__(self, status: Optional[int], message: str):
        self.status = status
        self.message = message
        full_message = f"HTTP {status} - {message}" if status else message
        super().__init__(full_message)


class ArgumentError(Exception):
    """Custom error class used for general argument exceptions"""

    def __init__(self, message: str):
        super().__init__(message)
