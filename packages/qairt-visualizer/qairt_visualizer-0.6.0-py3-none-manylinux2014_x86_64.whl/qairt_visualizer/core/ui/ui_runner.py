# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import argparse
import importlib
import os
import sys

from qairt_visualizer import view
from qairt_visualizer.core.launchers.electron_launcher_context import ElectronLauncherContext
from qairt_visualizer.core.ui.helpers.single_use_action import SingleUseAction


def run_qairt_visualizer():
    program_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        prog=program_name,
        description="\nQualcomm AI Runtime visualization application for AI "
        "models and runtime metrics. \n\n"
        "Running program without options will open full application "
        "while running with options will visualize the passed "
        "argument in its own window. \n\n",
        usage="%(prog)s [options] <model> <reports>",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=importlib.metadata.version(program_name),
        help="display %(prog)s version",
    )
    parser.add_argument("-m", "--model", type=str, help="Path to model to visualize", action=SingleUseAction)
    parser.add_argument(
        "-r", "--reports", metavar="STRING", nargs="+", help="List of report paths to visualize"
    )

    args = parser.parse_args()

    if args.model or args.reports:
        view(args.model, args.reports)
    else:
        ElectronLauncherContext().launch_standalone()
