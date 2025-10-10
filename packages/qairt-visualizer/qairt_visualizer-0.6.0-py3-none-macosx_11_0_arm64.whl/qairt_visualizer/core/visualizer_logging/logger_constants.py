# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Logger Constants"""

import logging

API_LOGGER: str = "visualizer.api"
WEB_SERVER_LOGGER: str = "visualizer.web-server"

api_logger = logging.getLogger(API_LOGGER)
web_server_logger = logging.getLogger(WEB_SERVER_LOGGER)
