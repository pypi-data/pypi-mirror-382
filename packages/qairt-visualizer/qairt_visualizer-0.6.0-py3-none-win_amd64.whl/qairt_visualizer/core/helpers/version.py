# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Extract Python Version"""

import platform
import sys


def main():
    """
    CLI entry point: Sends python version to stdout
    """
    sys.stdout.write(platform.python_version())
    sys.stdout.flush()


if __name__ == "__main__":
    main()
