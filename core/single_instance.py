import ctypes
import time
from ctypes import wintypes

MUTEX_NAME = "Local\\XYMYX-PC-Care"
WINDOW_TITLE = "XYMYX PC Care"
RESTART_WAIT_SECONDS = 10
RETRY_SECONDS = 0.2
ERROR_ALREADY_EXISTS = 183
ERROR_ACCESS_DENIED = 5
SW_RESTORE = 9


def kernel32():
    library = ctypes.WinDLL("kernel32", use_last_error=True)
    library.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    library.CreateMutexW.restype = wintypes.HANDLE
    library.CloseHandle.argtypes = [wintypes.HANDLE]
    return library


def try_acquire(name):
    library = kernel32()
    handle = library.CreateMutexW(None, False, name)
    error = ctypes.get_last_error()
    if handle and error != ERROR_ALREADY_EXISTS:
        return handle
    if handle:
        library.CloseHandle(handle)
    return None


def acquire(name=MUTEX_NAME, wait_seconds=0):
    deadline = time.monotonic() + wait_seconds
    while True:
        handle = try_acquire(name)
        if handle or time.monotonic() >= deadline:
            return handle
        time.sleep(RETRY_SECONDS)


def release(handle):
    kernel32().CloseHandle(handle)


def show_running_window(title=WINDOW_TITLE):
    user32 = ctypes.WinDLL("user32")
    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    window = user32.FindWindowW(None, title)
    if window:
        user32.ShowWindow(window, SW_RESTORE)
        user32.SetForegroundWindow(window)
    return bool(window)
