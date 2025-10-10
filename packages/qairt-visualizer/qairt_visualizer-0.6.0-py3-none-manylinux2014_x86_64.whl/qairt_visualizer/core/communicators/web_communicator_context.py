# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Web communicator"""

import aiohttp

from qairt_visualizer.core.communicators.base_communicator_context import (
    BaseCommunicatorContext,
)
from qairt_visualizer.core.errors import HttpError
from qairt_visualizer.schemas.view_schemas import ViewRequest


class WebCommunicatorContext(BaseCommunicatorContext):
    """
    Concrete communication class between the visualizer API and a visualizer web server.
    Responsible for connection management and message handling
    """

    async def send(self, request: ViewRequest) -> None:
        """
        Abstract method to send a message

        :param request: Request that will be sent
        """
        if request.id is None:
            self.logger.debug(
                "No window id received, cannot send view request. View Request: %s", request.model_dump()
            )
            raise ValueError("Unable to locate Visualizer window update with view.")

        window_id = request.id
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                http_addr = f"http://{self._host}:{self.port}/view/{window_id}"
                self.logger.debug("Sending view request to %s. Request: %s", http_addr, request.model_dump())

                async with session.post(http_addr, json=request.model_dump()) as response:
                    await response.json()
            except aiohttp.ClientResponseError as e:
                self.logger.debug(
                    "Http Error Status: %d. Message: %s. View request: %s.",
                    e.status,
                    e.message,
                    request.model_dump(),
                )
                if 400 <= e.status < 500:
                    raise HttpError(
                        e.status,
                        "There was an issue with your request. Please check it and try again.",
                    ) from e
                if 500 <= e.status < 600:
                    raise HttpError(
                        e.status,
                        "Could not open QAIRT Visualizer window, establishing connection for UI failed.",
                    ) from e
                raise HttpError(
                    e.status,
                    "An unexpected response from the Visualizer occurred.",
                ) from e
            except aiohttp.ClientError as e:
                raise HttpError(
                    None, "An error occurred when attempting to communicate with the Visualizer."
                ) from e
