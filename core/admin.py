import ctypes
import subprocess
import sys
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path

SETTINGS_OPTION = "--settings-folder"
USER_OPTION = "--original-user"
SHELL_EXECUTE_SUCCESS_ABOVE = 32
SHOW_NORMAL = 1


@dataclass(frozen=True)
class RestartOptions:
    settings_folder: str | None = None
    original_user: str | None = None


def is_admin():
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def current_user():
    buffer = ctypes.create_unicode_buffer(257)
    size = wintypes.DWORD(len(buffer))
    ctypes.windll.advapi32.GetUserNameW(buffer, ctypes.byref(size))
    return buffer.value


def option_value(arguments, name):
    if name in arguments:
        position = arguments.index(name) + 1
        if position < len(arguments):
            return arguments[position]
    return None


def parse_options(arguments):
    return RestartOptions(option_value(arguments, SETTINGS_OPTION), option_value(arguments, USER_OPTION))


def windowed_python(interpreter):
    candidate = Path(interpreter).with_name("pythonw.exe")
    return str(candidate) if candidate.exists() else str(interpreter)


def restart_command(settings_folder, user, frozen=None, executable=None, script=None):
    frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    executable = executable or sys.executable
    options = [SETTINGS_OPTION, str(settings_folder), USER_OPTION, user]
    if frozen:
        return str(executable), subprocess.list2cmdline(options)
    script = script or Path(sys.argv[0]).resolve()
    return windowed_python(executable), subprocess.list2cmdline([str(script), *options])


def shell_execute_as_admin(program, parameters):
    library = ctypes.WinDLL("shell32")
    library.ShellExecuteW.argtypes = [
        wintypes.HWND,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        ctypes.c_int,
    ]
    library.ShellExecuteW.restype = ctypes.c_void_p
    return library.ShellExecuteW(None, "runas", program, parameters, None, SHOW_NORMAL) or 0


def restart_as_admin(settings_folder, user, launcher=shell_execute_as_admin):
    program, parameters = restart_command(settings_folder, user)
    return launcher(program, parameters) > SHELL_EXECUTE_SUCCESS_ABOVE
