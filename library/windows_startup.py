# SPDX-License-Identifier: GPL-3.0-or-later

"""Manage the current user's Windows startup entry for the system monitor."""

import os
import subprocess
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "TuringSystemMonitor"
IS_WINDOWS = os.name == "nt"


def startup_command(main_directory: Path, executable=None, frozen=None) -> str:
    """Build a quoted command that starts the monitor without a console."""
    main_directory = Path(main_directory)
    executable = Path(executable or sys.executable)
    if frozen is None:
        frozen = getattr(sys, "frozen", False)

    if frozen:
        program = main_directory / ("main.exe" if IS_WINDOWS else "main")
        if not program.is_file():
            raise FileNotFoundError("Packaged main executable was not found: %s" % program)
        command_parts = [str(program)]
    else:
        script = main_directory / "main.py"
        pythonw = executable.with_name("pythonw.exe") if IS_WINDOWS else executable
        if IS_WINDOWS and not pythonw.is_file():
            pythonw = executable
        command_parts = [str(pythonw), str(script)]

    return subprocess.list2cmdline(command_parts)


def is_enabled():
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_QUERY_VALUE) as key:
            winreg.QueryValueEx(key, RUN_VALUE)
            return True
    except FileNotFoundError:
        return False


def set_enabled(enabled: bool, command=None, main_directory=None):
    """Add or remove this app's per-user Run entry (no admin rights needed)."""
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            if command is None:
                if main_directory is None:
                    raise ValueError("main_directory is required when command is omitted")
                command = startup_command(main_directory)
            winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, RUN_VALUE)
            except FileNotFoundError:
                pass
