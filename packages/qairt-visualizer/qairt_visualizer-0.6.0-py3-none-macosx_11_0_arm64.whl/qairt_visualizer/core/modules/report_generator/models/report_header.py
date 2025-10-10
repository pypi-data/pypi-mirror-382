# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Model for JSON report headers"""

from typing import Any

from pydantic import BaseModel, Field


class Version(BaseModel):
    """
    Class defining a Version schema
    """

    major: int
    minor: int
    patch: int


DEFAULT_HEADER_VERSION = Version(major=1, minor=0, patch=0)
DEFAULT_VERSION = Version(major=2, minor=0, patch=0)


class ReportHeader(BaseModel):
    """
    Class defining a ReportHeader schema
    """

    header_version: Version = Field(default_factory=lambda: DEFAULT_HEADER_VERSION)
    version: Version = Field(default_factory=lambda: DEFAULT_VERSION)
    artifact_type: str


class Report(BaseModel):
    """
    Class defining an Report schema
    """

    header: ReportHeader
    data: Any

    class Config:
        """
        Class defining the schema's configuration
        """

        extra = "forbid"
