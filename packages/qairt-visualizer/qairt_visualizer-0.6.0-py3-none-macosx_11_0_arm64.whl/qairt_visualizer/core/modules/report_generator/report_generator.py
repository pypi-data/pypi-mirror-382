# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Report Generator class"""

from typing import Any, Optional

from qairt_visualizer.core.modules.report_generator.models.report_header import Report, ReportHeader, Version


class ReportGenerator:
    """Utility class to generate QAIRT Visualizer consumable JSON reports"""

    def __init__(self):
        pass

    def generate_report(
        self, artifact_type: str, content: Any, header_version: Optional[Version], version: Optional[Version]
    ) -> Report:
        """
        Validates that an input file is a DLC file
        :param artifact_type: Path to the desired DLC file to open
        :param content: JSON serializable report content
        :param header_version: Optional header_version for the report
        :param version: Optional version for the report
        """
        report_header = ReportHeader(
            artifact_type=artifact_type, header_version=header_version, version=version
        )
        report = Report(header=report_header, data=content)
        return report

    def write_report_to_file(self, output_path: str, report: ReportHeader) -> None:
        """
        Writes the input report out as a serialized JSON
        :param output_path: Path to output the JSON report
        :param report: The JSON report to serialize into a file
        """
        raise NotImplementedError()
