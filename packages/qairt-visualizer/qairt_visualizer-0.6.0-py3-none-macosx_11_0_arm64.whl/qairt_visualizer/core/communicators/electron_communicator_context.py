# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Electron communicator"""

from typing import Any
from uuid import uuid4

import zmq.asyncio
from pydantic import ValidationError
from zmq.asyncio import Context, Poller, Socket

from qairt_visualizer.core.communicators.base_communicator_context import (
    BaseCommunicatorContext,
)
from qairt_visualizer.core.errors import ReceiveError
from qairt_visualizer.schemas.view_schemas import ViewRequest, ViewResponse


class ElectronCommunicatorContext(BaseCommunicatorContext):
    """
    Concrete communication class between the visualizer API and visualizer Electron application.
    Responsible for connection management and message handling
    """

    def __init__(self):
        """
        Intializes the Electron Communicator class
        """
        self._ctx = Context.instance()
        self._READY: str = "ready"  # pylint: disable=invalid-name
        self._ERROR: str = "error"  # pylint: disable=invalid-name
        super().__init__()

    async def _is_socket_ready(self, socket: zmq.asyncio.Socket, maximum_retries: int = 2) -> bool:
        """
        Establishes a ZeroMQ connection by sending a 'ready' message to and waits for an acknowledgement from
        a node. Returns whether or not an acknowledgement is received within the given amount of
        maximum retries.

        :param socket: The socket object to make handshake with
        :param maximum_retries: Max amount of times to attempt handshake
        """
        for attempt in range(maximum_retries):
            self.logger.debug("Handshake attempt %d/%d", attempt + 1, maximum_retries)
            events = await self._send_message(socket, self._READY)
            if events:
                msg = await socket.recv()
                if msg == self._READY.encode("utf-8"):
                    return True
        return False

    async def _send_message(self, socket: Socket, msg: str, timeout: int = 5000) -> list[tuple[Any, int]]:
        poller = Poller()
        poller.register(socket, zmq.POLLIN)
        socket.send_string(msg)
        return await poller.poll(timeout=timeout)

    async def send(self, request: ViewRequest) -> None:
        connect_addr = f"tcp://{self._host}:{self.port}"
        socket_identity = str(uuid4())
        socket = self._ctx.socket(zmq.DEALER)
        socket.setsockopt_string(zmq.IDENTITY, socket_identity)
        self.logger.debug("Connecting to socket. Address: %s, Identity: %s", connect_addr, socket_identity)
        socket.connect(connect_addr)
        try:
            self.logger.info("Verifying UI is ready to receive view request.")
            self.logger.debug("ViewRequest: %s", request.model_dump())
            socket_ready = await self._is_socket_ready(socket)
            if not socket_ready:
                self.logger.debug(
                    "Handshake attempt failed. Exceeded maximum number of attempts to make "
                    "connection with Visualizer."
                )
                raise RuntimeError(
                    "Could not open QAIRT Visualizer window, establishing connection for UI failed."
                )

            events = await self._send_message(socket, request.model_dump_json(), timeout=5000)
            if events:
                response = await self.receive(socket)
                if response.status == self._ERROR:
                    self.logger.error("Error: %s, Request: %s", response.message, request.model_dump())
        finally:
            self.logger.debug("Closing socket id: %s", socket_identity)
            socket.close()

    async def receive(self, socket: Socket) -> ViewResponse:
        """
        Method used to receive and deserialize a message on the given socket

        :param socket: Instance of the communication socket
        """
        msg = await socket.recv()
        decoded_msg = msg.decode("utf-8")
        try:
            response = ViewResponse.model_validate_json(decoded_msg)
            self.logger.debug("Received response from Visualizer: %s", response.model_dump())
            return response
        except ValidationError as exc:
            raise ReceiveError("Unable to validate response from Visualizer", decoded_msg) from exc
