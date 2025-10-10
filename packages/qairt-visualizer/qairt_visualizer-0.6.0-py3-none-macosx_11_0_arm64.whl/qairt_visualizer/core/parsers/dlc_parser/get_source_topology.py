# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Extract Source Topology From DLC"""

import sys
import tempfile

from qairt_visualizer.core.parsers.dlc_parser.dlc_parser import DlcParser
from qairt_visualizer.core.parsers.dlc_parser.helpers.exception_helpers import handle_exception


def main():
    """
    CLI entry point: Gets the DLC's topology, if available.
    """
    if len(sys.argv) == 1:
        raise ValueError("An argument for a DLC file path was not provided")
    dlc_path = sys.argv[1]

    reader = DlcParser(dlc_path)
    source_topology = reader.get_source_topology()

    sys.stdout.write(save_topology_to_tmp(source_topology))
    sys.stdout.flush()


def save_topology_to_tmp(topology) -> str:
    """
    Saves the graph topology to a temp file, which must be removed by the caller
    :param topology: The binary topology data to save to file
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".onnx", mode="wb") as tmp:
            tmp.write(topology)
            return tmp.name
    except Exception as e:  # pylint: disable=broad-exception-caught
        handle_exception(e)
        return ""


if __name__ == "__main__":
    main()
