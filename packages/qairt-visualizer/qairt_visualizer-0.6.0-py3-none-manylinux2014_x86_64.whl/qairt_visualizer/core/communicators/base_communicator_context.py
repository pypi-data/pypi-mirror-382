# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Communicator base class"""

from abc import ABC, abstractmethod

from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.schemas.view_schemas import ViewRequest


class BaseCommunicatorContext(ABC):
    """
    Abstract base class for communication. Responsible for connection management and
    message handling
    """

    def __init__(self):
        """
        Initializes the Communicator class
        """
        self._host: str = "localhost"
        self.port: int = 5555
        self.logger = api_logger

    @abstractmethod
    async def send(self, request: ViewRequest) -> None:
        """
        Abstract method to send a message

        :param request: Request that will be sent
        """
