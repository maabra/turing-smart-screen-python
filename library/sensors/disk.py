# SPDX-License-Identifier: GPL-3.0-or-later
#
# Select the OS volume for disk capacity sensors. On Windows, '/' is not a
# reliable way to express the system volume; use the configured system drive.

import os


def usage_path() -> str:
    """Return the root of the OS volume used for disk capacity metrics."""
    if os.name == "nt":
        system_drive = os.environ.get("SystemDrive")
        if system_drive:
            return system_drive + os.sep
    return os.path.abspath(os.sep)
