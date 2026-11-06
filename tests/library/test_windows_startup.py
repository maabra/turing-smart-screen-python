import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from library import windows_startup


class TestStartupCommand(unittest.TestCase):
    def test_source_command_uses_pythonw_and_quotes_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "Turing Monitor"
            root.mkdir()
            pythonw = Path(temp_dir) / "Python" / "pythonw.exe"
            pythonw.parent.mkdir()
            pythonw.touch()

            with patch("library.windows_startup.IS_WINDOWS", True):
                command = windows_startup.startup_command(
                    root, executable=pythonw.with_name("python.exe"), frozen=False
                )

            self.assertEqual(
                command,
                subprocess.list2cmdline([str(pythonw), str(root / "main.py")]),
            )

    def test_packaged_command_targets_main_exe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            main_exe = root / "main.exe"
            main_exe.touch()

            with patch("library.windows_startup.IS_WINDOWS", True):
                command = windows_startup.startup_command(root, frozen=True)

            self.assertEqual(command, subprocess.list2cmdline([str(main_exe)]))

    def test_packaged_command_reports_missing_main_exe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("library.windows_startup.IS_WINDOWS", True):
                with self.assertRaises(FileNotFoundError):
                    windows_startup.startup_command(Path(temp_dir), frozen=True)


if __name__ == "__main__":
    unittest.main()
