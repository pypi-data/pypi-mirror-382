# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Web Launcher Context"""

import asyncio
import subprocess
import sys
from pathlib import Path

import aiohttp
import psutil
from IPython.display import HTML, display

from qairt_visualizer.core.launchers.base_ui_launcher_context import BaseUILauncherContext
from qairt_visualizer.core.launchers.models.process_attributes import ProcessAttributes
from qairt_visualizer.helpers.ui_helpers import find_ui_path_to


class WebLauncherContext(BaseUILauncherContext):
    """
    Concrete launcher class responsible for launching the the visualizer web server.
    """

    def __init__(self):
        super().__init__()
        self._host = "localhost"
        self.application_name = "visualizer_web_server.py"

    def launch(self):
        port = self.detect_port(5555)
        server_path = find_ui_path_to(self.application_name)
        cmd = [
            sys.executable,
            str(server_path),
            "--port",
            str(port),
        ]
        self.logger.debug("Launching Visualizer web server")
        self.logger.debug("Launch command: %s", cmd)
        # pylint: disable=consider-using-with
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(Path(__file__).parent)
        )
        self.set_pid(proc.pid)
        return port

    async def wait_for_server(self, port: int, ping_retries: int = 25):
        """
        Pings server for ping_retries amount of times until it receives a 200. If ping_retries is
        exceeded, RuntimeError is raised.
        :param port: Port to ping server on
        :param ping_retries: Amount of times to try pinging server, defaults to 5
        """
        for attempt in range(ping_retries):
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                try:
                    self.logger.debug("Ping attempt %d/%d", attempt + 1, ping_retries)
                    async with session.get(f"http://{self._host}:{port}/status", timeout=2000) as response:
                        await response.json()
                        return
                except (aiohttp.ClientError, aiohttp.ClientResponseError, asyncio.TimeoutError) as e:
                    if attempt == 0:
                        self.logger.warning("Waiting on response from Visualizer UI...")
                    else:
                        self.logger.debug(
                            "No response received from Visualizer UI. Attempting retry %d/%d",
                            attempt + 1,
                            ping_retries,
                        )
                    self.logger.debug(e)

                await asyncio.sleep(0.05)
        friendly_error = "Couldn't establish connection with Visualizer"
        self.logger.error(friendly_error)
        raise RuntimeError(friendly_error)

    def embed_frontend(self, port: int):
        """
        Responsible for displaying Visualizer application
        :param port: Port webserver is running on
        """
        self.logger.debug("View window id: %s", self.id)
        display(
            HTML(
                f"""
                 <iframe src="http://{self._host}:{port}/#/workspaces/{self.id}?mode=jupyter"
                 width="100%" height="500px"></iframe>
                 """
            )
        )

    def is_same_process(self, process_attrs: ProcessAttributes, process_name: str):
        cmdline = process_attrs.cmdline
        return len(cmdline) > 2 and "python" in process_attrs.proc_name and process_name in cmdline[1]

    def extract_port_from_process(self, process_attrs: ProcessAttributes) -> int:
        try:
            cmdline = process_attrs.cmdline
            if not cmdline:
                return self._PROCESS_NOT_FOUND
            if self.is_same_process(process_attrs, self.application_name):
                self.logger.debug("Found visualizer process. Attempting to extract port.")
                if "--port" in cmdline:
                    port_index = cmdline.index("--port") + 1
                    if port_index < len(cmdline):
                        port = cmdline[port_index]
                        return int(port)
                self.logger.debug("Couldn't extract port argument. CMD line args: %s", cmdline)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            self.logger.debug(e)

        return self._PROCESS_NOT_FOUND

    def get_ui_process_search_command_for_windows(self, process_name: str) -> str:
        return f"""
            Get-CimInstance Win32_Process | `
            Where-Object {{ ($_.CommandLine -split ' ')[1] -match '{process_name}' }} | `
            Select-Object -First 1 ProcessId, Name, CommandLine | `
            ConvertTo-Json
        """

    async def after_launch_tasks(self, port: int) -> None:
        self.logger.debug("Waiting for UI")
        await self.wait_for_server(port)

        self.embed_frontend(port)
