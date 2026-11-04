import base64
import ctypes
import subprocess
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 60
OUTPUT_AS_UTF8 = "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"


class PowerShellError(Exception):
    pass


def powershell_path():
    buffer = ctypes.create_unicode_buffer(260)
    ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
    return Path(buffer.value) / "WindowsPowerShell" / "v1.0" / "powershell.exe"


def run_powershell(script, timeout=DEFAULT_TIMEOUT_SECONDS):
    encoded = base64.b64encode((OUTPUT_AS_UTF8 + script).encode("utf-16-le")).decode("ascii")
    command = [
        str(powershell_path()),
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-EncodedCommand",
        encoded,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except subprocess.TimeoutExpired as error:
        raise PowerShellError("timeout") from error
    except OSError as error:
        raise PowerShellError(str(error)) from error
    if result.returncode != 0:
        raise PowerShellError(result.stderr.strip())
    return result.stdout
