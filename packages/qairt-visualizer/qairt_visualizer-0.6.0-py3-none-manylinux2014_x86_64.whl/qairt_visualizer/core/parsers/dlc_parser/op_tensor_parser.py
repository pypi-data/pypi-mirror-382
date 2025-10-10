# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""DLC Op and Tensor Parsing"""

import sys

from qairt_visualizer.core.modules.report_generator.models.report_header import Report, ReportHeader
from qairt_visualizer.core.parsers.dlc_parser.dlc_parser import DlcParser
from qairt_visualizer.core.parsers.dlc_parser.helpers.exception_helpers import handle_exception


def main():
    """
    CLI entry point: Gets the DLC's ops and tensors, if available.
    """
    try:
        if len(sys.argv) == 1:
            raise ValueError("An argument for a DLC file path was not provided")
        dlc_path = sys.argv[1]
        reader = DlcParser(dlc_path)
        mapping_info = reader.extract_onnx_mappings()
        report = Report(header=ReportHeader(artifact_type="OP_TENSOR_MAPPINGS"), data=mapping_info)
        print(report.model_dump_json(indent=2))
    except Exception as e:  # pylint: disable=broad-exception-caught
        handle_exception(e)


if __name__ == "__main__":
    main()
