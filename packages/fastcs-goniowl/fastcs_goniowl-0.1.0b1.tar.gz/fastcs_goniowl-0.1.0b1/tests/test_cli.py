import subprocess
import sys

from fastcs_goniowl import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "fastcs_goniowl", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
