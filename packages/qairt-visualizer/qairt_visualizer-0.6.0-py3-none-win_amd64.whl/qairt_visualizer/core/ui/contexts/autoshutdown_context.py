# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""AutoShutdown Context"""

import asyncio
import os
import platform
import signal
from typing import Callable, Optional

from qairt_visualizer.core.visualizer_logging.logger_constants import web_server_logger
from qairt_visualizer.helpers.asyncio_helpers import has_event_loop_running


class AutoShutdownContext:
    """
    AutoShutdownContext manages automatically shutting down the webserver based on the should
    shutdown callback
    """

    def __init__(self, timeout_seconds: int, should_shutdown_callback: Callable[[], bool]):
        self.shutdown_timer: Optional[asyncio.TimerHandle] = None
        self._timeout_seconds = timeout_seconds
        self._should_shutdown = should_shutdown_callback
        self.logger = web_server_logger

    def reset_shutdown_timer(self) -> None:
        """
        Cancels any existing shutdown timers and starts a new timer for shutdown
        """
        if self.shutdown_timer:
            self.logger.debug("Canceling existing shutdown timer")
            self.shutdown_timer.cancel()
        self.logger.debug("Resetting shutdown timer")

        if platform.system().lower() == "windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore

        if has_event_loop_running():
            loop = asyncio.get_running_loop()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.shutdown_timer = loop.call_later(self._timeout_seconds, self.shutdown)

    def shutdown(self):
        """
        If the _should_shutdown callback is true, this function sends a termination signal to the current
        process to shutdown server gracefully. Otherwise, the shutdown timer is reset.
        """
        if self._should_shutdown():
            self.logger.info(
                "Due to inactivity exceeding the maximum timeout period, "
                "the web server will now shut down automatically."
            )
            if has_event_loop_running():
                asyncio.get_running_loop().close()
            os.kill(os.getpid(), signal.SIGTERM)
        else:
            self.reset_shutdown_timer()
