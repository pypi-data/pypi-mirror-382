# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Post install helper module given some files have licensing issue to package with wheel"""

import os
import platform
import shutil
import ssl
import subprocess
import tempfile
from importlib.resources import files
from typing import List

import click
import requests

from qairt_visualizer.core.visualizer_logging.logger_constants import api_logger
from qairt_visualizer.core.visualizer_logging.logging_config import LoggingConfig


def is_arm_64(arch_name):
    return arch_name in ["aarch64", "arm64"]


def is_x86_64(arch_name):
    return arch_name in ["x86_64", "amd64"]


class DownloadInfo(object):
    ELECTRON_VERSION = "30.5.1"
    URL_BASE = f"https://github.com/electron/electron/releases/download/v{ELECTRON_VERSION}/"
    UI_DEST_PATH = str(files("qairt_visualizer.core.ui").joinpath("dist"))
    ZIP_EXTRACT_DEST = UI_DEST_PATH
    ZIP_FILES_TO_REMOVE = ["electron", "resources", "version"]
    ZIP_FILES_TO_REMOVE_WIN = ["electron.exe", "resources", "version"]
    ZIP_FILES_TO_COPY = ["."]  # get everything else in zip after removing above
    ZIP_FILES_TO_REMOVE_MAC: List[str] = []  # we will only copy one dir from mac, nothing to specify here
    ZIP_FILES_TO_COPY_MAC = [
        os.path.join("Electron.app", "Contents", "Frameworks", "Electron Framework.framework")
    ]
    ZIP_EXTRACT_DEST_MAC = os.path.join(
        UI_DEST_PATH, "qairt_visualizer.app", "Contents", "Frameworks", "Electron Framework.framework"
    )

    def __init__(
        self, file_to_download, zip_extract_dest, zip_files_to_copy, zip_files_to_remove, verify_path
    ):
        """

        :param file_to_download: url path to download
        :param zip_extract_dest: the final location of where the downloaded file should be extracted to
               (note: only files under zip_files_to_copy will be copied to this dest)
        :param zip_files_to_remove: the list of files to remove from the extracted zip.
        :param zip_files_to_copy: the list of files to copy  out of the extracted zip into dest after doing
        removal from zip (if any)
        :param verify_path: The path to use for verifying that extraction is done correctly additionally,
        used to determine if post install is needed
        """
        self.url = self.URL_BASE + "/" + file_to_download
        self.file_download_path = os.path.join(self.UI_DEST_PATH, file_to_download)
        self.zip_extract_dest = zip_extract_dest
        self.zip_files_to_remove = zip_files_to_remove
        self.zip_files_to_copy = zip_files_to_copy
        self.verify_path = verify_path


def get_download_info():
    zip_extract_dest = DownloadInfo.ZIP_EXTRACT_DEST
    zip_files_to_copy = DownloadInfo.ZIP_FILES_TO_COPY
    zip_files_to_remove = DownloadInfo.ZIP_FILES_TO_REMOVE
    os_name = platform.system().lower()
    arch_name = platform.machine().lower()
    if os_name == "windows" and is_arm_64(arch_name):
        # We currently don't support native windows arm because of dependency support gap for windows on arm
        # hence, get win32 electron artifacts
        file_to_download = f"electron-v{DownloadInfo.ELECTRON_VERSION}-win32-x64.zip"
        verify_path = os.path.join(DownloadInfo.UI_DEST_PATH, "ffmpeg.dll")
        zip_files_to_remove = DownloadInfo.ZIP_FILES_TO_REMOVE_WIN
    elif os_name == "windows" and is_x86_64(arch_name):
        file_to_download = f"electron-v{DownloadInfo.ELECTRON_VERSION}-win32-x64.zip"
        verify_path = os.path.join(DownloadInfo.UI_DEST_PATH, "ffmpeg.dll")
        zip_files_to_remove = DownloadInfo.ZIP_FILES_TO_REMOVE_WIN
    elif os_name == "linux" and is_x86_64(arch_name):
        file_to_download = f"electron-v{DownloadInfo.ELECTRON_VERSION}-linux-x64.zip"
        verify_path = os.path.join(DownloadInfo.UI_DEST_PATH, "libffmpeg.so")
    elif os_name == "linux" and is_arm_64(arch_name):
        file_to_download = f"electron-v{DownloadInfo.ELECTRON_VERSION}-linux-arm64.zip"
        verify_path = os.path.join(DownloadInfo.UI_DEST_PATH, "libffmpeg.so")
    elif os_name == "darwin" and is_arm_64(arch_name):
        file_to_download = f"electron-v{DownloadInfo.ELECTRON_VERSION}-darwin-arm64.zip"
        zip_extract_dest = DownloadInfo.ZIP_EXTRACT_DEST_MAC
        zip_files_to_copy = DownloadInfo.ZIP_FILES_TO_COPY_MAC
        zip_files_to_remove = DownloadInfo.ZIP_FILES_TO_REMOVE_MAC
        verify_path = os.path.join(DownloadInfo.ZIP_EXTRACT_DEST_MAC, "Libraries", "libffmpeg.dylib")
    else:
        raise RuntimeError(
            f"Unable to load UI, os and arch combo not supported. Got os_name: "
            f"{os_name}, arch_name: {arch_name}"
        )

    return DownloadInfo(
        file_to_download, zip_extract_dest, zip_files_to_copy, zip_files_to_remove, verify_path
    )


def run():
    """
    Fetch electron given not part of distributable wheel
    """
    LoggingConfig.setup_logging()

    def _download_and_extract_electron(ssl_cert_verify=None):
        response = requests.get(url=download_info.url, stream=True, verify=ssl_cert_verify)
        if response.status_code == 200:
            with open(download_info.file_download_path, "wb") as file:
                file.write(response.content)
        else:
            raise RuntimeError("Get requested failed")

        with tempfile.TemporaryDirectory() as tmp_dir:
            # unzip to temp location first to remove un-necessary files
            # Linux/Unix zip is typically standard for zip files, in windows surprisingly tar is used
            # to extract zip files.
            unzip_platform_default_cmd = f'unzip "{download_info.file_download_path}" -d "{tmp_dir}"'
            if platform.system().lower() == "windows":
                unzip_platform_default_cmd = f'tar -xf "{download_info.file_download_path}" -C "{tmp_dir}"'
            subprocess.run(
                unzip_platform_default_cmd,
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            for content in download_info.zip_files_to_remove:
                content_abs_path = os.path.join(tmp_dir, content)
                if os.path.isdir(content_abs_path):
                    shutil.rmtree(content_abs_path)
                else:
                    os.remove(content_abs_path)
            for src, dest in zip(
                download_info.zip_files_to_copy,
                [download_info.zip_extract_dest] * len(download_info.zip_files_to_copy),
            ):
                shutil.copytree(os.path.join(tmp_dir, src), dest, dirs_exist_ok=True, symlinks=True)
            if not os.path.exists(download_info.verify_path):
                raise RuntimeError(
                    f"Failed to verify post install expected files at {download_info.zip_extract_dest}"
                )

    download_info = get_download_info()
    # Only do fetch if first time loading and if skipping post install is not requested
    if (
        not (os.path.exists(download_info.verify_path) and os.path.exists(download_info.file_download_path))
        and os.getenv("SKIP_POST_INSTALL", "false").lower() == "false"
    ):
        try:
            verify = (
                ssl.get_default_verify_paths().cafile
                if os.getenv("REQUEST_VERIFY", "true").lower() == "true"
                else False
            )
            try:
                _download_and_extract_electron(ssl_cert_verify=verify)
            except requests.exceptions.SSLError:
                api_logger.warning("Unable to do post install due to ssl cert verification error.")
                if click.confirm(
                    "Would you like to disable ssl cert verification for post install?",
                    default=None,
                    abort=True,
                    err=True,
                ):
                    _download_and_extract_electron(ssl_cert_verify=False)
                else:
                    raise RuntimeError(
                        "Unable to load UI, post install setup failed to fetch files due to "
                        "inability to verify ssl certs. If you would like to disable cert "
                        "checking, set environment variable REQUEST_VERIFY=false"
                    ) from None
        except BaseException:
            raise RuntimeError("Unable to load UI, post install setup failed to fetch files.")
