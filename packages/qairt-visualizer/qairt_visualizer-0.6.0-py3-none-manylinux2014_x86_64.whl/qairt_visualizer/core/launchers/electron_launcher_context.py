# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Electron launcher"""

import os
import platform
import subprocess
import time
from pathlib import Path
from typing import List, Optional, cast

from qairt_visualizer.core.launchers.base_ui_launcher_context import BaseUILauncherContext
from qairt_visualizer.core.launchers.models.process_attributes import ProcessAttributes
from qairt_visualizer.helpers.ui_helpers import find_ui_path_to


class ElectronLauncherContext(BaseUILauncherContext):
    """
    Concrete launcher class responsible for launching the Electron Visualization application.
    """

    _DEFAULT_PORT = 5555
    _PORT_FILE_LOCATION = os.path.expanduser("~/.qairt_visualizer/current_port.txt")

    def __init__(self):
        super().__init__()
        self.application_name = "qairt_visualizer"

    def _get_electron_path(self, caller_platform: str) -> str:
        app_extension = ""
        if caller_platform == "windows":
            app_extension = ".exe"
        elif caller_platform == "darwin":
            app_extension = ".app"
        return find_ui_path_to(f"dist/{self.application_name}{app_extension}")

    def is_same_process(self, process_attrs: ProcessAttributes, process_name: str) -> bool:
        return process_attrs.proc_name == process_name

    def launch(self) -> int:
        """Launches application in background at given port
        :return: The port Visualizer is listening on
        """
        process_attrs, existing_port = self.locate_ui_process()

        visual_only_launched_previously_application_listening_for_connection = (
            process_attrs is not None and existing_port != -1
        )
        if visual_only_launched_previously_application_listening_for_connection:
            return existing_port

        port_written_to_port_file = self._get_existing_zmq_port()
        main_app_launched_listening_for_connection = (
            process_attrs is not None and port_written_to_port_file is not None
        )

        if main_app_launched_listening_for_connection:
            return cast(int, port_written_to_port_file)

        has_stale_port_file = (
            process_attrs is None and port_written_to_port_file is not None and self._is_port_file_old()
        )
        # This block handles when another python script may have launched
        # visualizer while the above code already ran
        if has_stale_port_file:
            try:
                port_file = Path(self._PORT_FILE_LOCATION)
                port_file.unlink(missing_ok=True)
                self.logger.debug("Deleted stale port file")
            except OSError as e:
                self.logger.error("Failed to delete stale port file: %s", e)
        elif port_written_to_port_file is not None:
            return port_written_to_port_file
        # End handler for multi-python script scenario

        port = self.detect_port(self._DEFAULT_PORT)
        self._launch(["--port", f"{port}"])
        return port

    def launch_standalone(self) -> None:
        """Launches full application"""
        self._launch([])

    def _launch(self, extra_args: List[str]) -> None:
        p = platform.system().lower()
        if p == "darwin":
            extra_args = ["--args"] + extra_args if extra_args else extra_args
            command_line_args = ["open", "-a", self._get_electron_path(p)] + extra_args
        else:
            command_line_args = [self._get_electron_path(p)] + extra_args

        self.logger.debug("Launching Visualizer application.")
        self.logger.debug("Launch command: %s", command_line_args)
        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            command_line_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.set_pid(proc.pid)

    def _get_existing_zmq_port(self) -> Optional[int]:
        """Check for existing ZMQ port from temp file"""
        try:
            if os.path.exists(self._PORT_FILE_LOCATION):
                with open(self._PORT_FILE_LOCATION, "r", encoding="utf-8") as f:
                    port = int(f.read().strip())
                    self.logger.debug("Found existing ZMQ port: %s", port)
                    return port
        except (ValueError, IOError, OSError) as e:
            self.logger.debug("Could not read port file: %s", e)

        return None

    def _is_port_file_old(self, seconds: int = 30) -> bool:
        """Check if the port file is older than the specified number of seconds"""
        try:
            if not os.path.exists(self._PORT_FILE_LOCATION):
                return False

            file_mod_time = os.path.getmtime(self._PORT_FILE_LOCATION)
            current_time = time.time()
            age_in_seconds = current_time - file_mod_time

            return age_in_seconds > seconds

        except OSError as e:
            self.logger.debug("Error checking port file age: %s", e)
            return False

    def extract_port_from_process(self, process_attrs: ProcessAttributes) -> int:
        app_extension = ""
        process_name = self.application_name

        if platform.system().lower() == "windows":
            app_extension = ".exe"

        process_name = process_name + app_extension
        cmdline = process_attrs.cmdline
        if self.is_same_process(process_attrs, process_name):
            if cmdline and "--port" in cmdline:
                port_index = cmdline.index("--port") + 1
                if port_index < len(cmdline):
                    port = cmdline[port_index]
                    return int(port)
            self.logger.debug("Couldn't extract port argument. CMD line args: %s", cmdline)
        return -1

    def get_ui_process_search_command_for_windows(self, process_name: str) -> str:
        return f"""
            Get-CimInstance Win32_Process | `
            Where-Object {{ $_.Name -match '{process_name}' }} | `
            Select-Object -First 1 ProcessId, Name, CommandLine | `
            ConvertTo-Json
        """

    async def after_launch_tasks(self, port: int) -> None:
        pass
