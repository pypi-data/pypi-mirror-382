# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""UI launcher base class"""

import errno
import json
import platform
import socket
import subprocess
import threading
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from uuid import uuid4

import psutil

from qairt_visualizer.core.launchers.models.process_attributes import ProcessAttributes
from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.helpers.string_helpers import is_none_or_empty


class BaseUILauncherContext(ABC):
    """
    Abstract base class for all UI launchers
    """

    _lock = threading.Lock()
    _pid: Optional[int] = None
    _PROCESS_NOT_FOUND = -1

    def __init__(self):
        self.id = str(uuid4())
        self.logger = api_logger
        self.application_name = ""

    def _find_open_port(self, s: socket.socket) -> int:
        """
        Returns an open port on the given socket

        :param s: Socket used to find the open port on
        """
        s.bind(("localhost", 0))
        open_port = s.getsockname()[1]
        return open_port

    def _find_ui_process_port_by_iteration(self) -> Tuple[Optional[ProcessAttributes], int]:
        for proc in psutil.process_iter(["name", "pid", "cmdline"]):
            try:
                process_attrs = ProcessAttributes.parse_from_process(proc)
                port = self.extract_port_from_process(process_attrs)
                if port > -1:
                    return process_attrs, port
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                self.logger.debug(e)

        return None, self._PROCESS_NOT_FOUND

    def _find_ui_process_port_windows(self, process_name: str) -> Tuple[Optional[ProcessAttributes], int]:
        cmd = self.get_ui_process_search_command_for_windows(process_name)
        self.logger.debug("Search command: %s", cmd)
        try:
            process = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)  # pylint: disable=subprocess-run-check
        except FileNotFoundError:
            self.logger.debug("Powershell not found. Attempting direct process iteration...")
            return self._find_ui_process_port_by_iteration()

        search_crashed_or_exited_unexpectedly = process.returncode != 0
        if search_crashed_or_exited_unexpectedly:
            self.logger.warning("There was an issue locating the Visualizer UI.")
            return None, self._PROCESS_NOT_FOUND

        process_info = process.stdout.strip()
        if is_none_or_empty(process_info):
            return None, self._PROCESS_NOT_FOUND

        res = json.loads(process_info)
        pid = res.get("ProcessId", None)
        cmdline = res.get("CommandLine", "").split(" ")
        name = res.get("Name", None)
        process_attrs = ProcessAttributes(cmdline=cmdline, pid=pid, proc_name=name)
        port = self.extract_port_from_process(process_attrs)
        return process_attrs, port

    def detect_port(self, default_port: int) -> int:
        """
        Checks if default_port is open and returns it. If it's not open, this function attempts to find an
        open port and returns it

        :param default_port: A default port to first check
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", default_port))
                return s.getsockname()[1]
            except OSError as e:
                if e.errno == errno.EADDRINUSE:
                    return self._find_open_port(s)
                raise

    def find_ui_process_port_using_pid(self, pid: int) -> int:
        """
        Searches for a UI process using the given PID and attempts to extract the
        port it's listening on.

        :param pid: The PID to extract the port argument from
        :return: The port number for the existing process, -1 if cannot be found
        """
        try:
            process: psutil.Process = psutil.Process(pid)
            return self.extract_port_from_process(
                ProcessAttributes(process.cmdline(), process.name(), pid=pid)
            )
        except psutil.NoSuchProcess:
            return self._PROCESS_NOT_FOUND

    def find_ui_process_port(self) -> int:
        """
        Searches for a UI process using the application_name. If _pid is set, this function will attempt to
        extract the port from that process first.
        :return: The port number for the existing process, -1 if cannot be found
        """
        process_attrs, port = self.locate_ui_process()
        if self._pid:
            if port is not self._PROCESS_NOT_FOUND:
                return port

        if process_attrs is None or port == self._PROCESS_NOT_FOUND:
            return self._PROCESS_NOT_FOUND

        self.set_pid(process_attrs.pid)
        return port

    def locate_ui_process(self) -> Tuple[ProcessAttributes | None, int]:
        """
        Will loop through all running processes and checks if any of them match the application_name provided
        If a process is found, both process attributes and the port number is extracted. If _pid is set,
        this function will attempt to locate the process and parse it to return process attributes and port.
        :return: A tuple containing the ProcessAttributes and the port number
        """
        port = None
        process_attrs = None
        if self._pid:
            try:
                process: psutil.Process = psutil.Process(self._pid)
                process_attrs = ProcessAttributes(process.cmdline(), process.name(), pid=self._pid)
                port = self.extract_port_from_process(process_attrs)
            except psutil.NoSuchProcess:
                process_attrs, port = [None, self._PROCESS_NOT_FOUND]

        if port is not None and port is not self._PROCESS_NOT_FOUND:
            return process_attrs, port

        if platform.system().lower() == "windows":
            process_name = self.application_name
            process_attrs, port = self._find_ui_process_port_windows(process_name)
        else:
            process_attrs, port = self._find_ui_process_port_by_iteration()
        return process_attrs, port

    @classmethod
    def set_pid(cls, pid: int) -> None:
        """Sets the pid class variable

        :param pid: The PID to set the _pid variable to
        """
        with cls._lock:
            cls._pid = pid

    @abstractmethod
    def launch(self) -> int:
        """
        Used to launch a UI
        :return: The port the UI app launched on
        """

    @abstractmethod
    def extract_port_from_process(self, process_attrs: ProcessAttributes) -> int:
        """
        Extracts the port number from process attributes.

        This function retrieves the port argument from process attributes, provided the ProcessAttributes
        are for the given process_name.
        :param process_attrs: Process attributes to check against
        :return: The port number for the existing process, -1 if cannot be found
        """

    @abstractmethod
    async def after_launch_tasks(self, port: int) -> None:
        """
        Performs actions after the main launch execution.

        This method is intended to be overridden by subclasses to define specific
        tasks that need to be executed after the primary launch or process has
        completed.
        :param port: Port that launched process can be found on
        """

    @abstractmethod
    def is_same_process(self, process_attrs: ProcessAttributes, process_name: str) -> bool:
        """
        Verifies the given process attributes are a match for the process name
        :return: True if it's the same process, False if not
        """

    @abstractmethod
    def get_ui_process_search_command_for_windows(self, process_name: str) -> str:
        """
        Responsible for creating the search command used to locate the Visualizer UI on Windows
        :param process_name: The process name to search for
        :return: Search command used for locating Visualizer UI
        """
