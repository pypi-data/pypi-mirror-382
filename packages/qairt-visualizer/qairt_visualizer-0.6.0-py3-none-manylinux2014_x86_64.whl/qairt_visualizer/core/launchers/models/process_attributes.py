# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""ProcessAttributes class"""

from dataclasses import dataclass
from typing import List

import psutil


@dataclass
class ProcessAttributes:
    """Process Attributes"""

    cmdline: List[str]
    proc_name: str
    pid: int

    @classmethod
    def parse_from_process(cls, process: psutil.Process) -> "ProcessAttributes":
        """
        Parses a process and sets instance variables accordingly

        :param process: The process to parse
        """
        has_info = hasattr(process, "info")
        cmdline = process.info.get("cmdline", []) if has_info else process.cmdline()
        pid = process.info.get("pid") if has_info else process.pid()
        proc_name = process.info.get("name", None) if has_info else process.name()
        return cls(cmdline=cmdline, pid=pid, proc_name=proc_name)
