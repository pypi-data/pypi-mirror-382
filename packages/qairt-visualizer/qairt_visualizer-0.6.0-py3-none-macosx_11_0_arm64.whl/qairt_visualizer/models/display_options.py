# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Model providing optional view() call options"""

from pydantic import BaseModel, ConfigDict


# Implement additional option(s) in https://jira-dc.qualcomm.com/jira/browse/AISW-119343
class DisplayOptions(BaseModel):
    """List of Window view() call options"""

    model_config = ConfigDict(extra="forbid")
    use_same_workspace: bool = True
