import ctypes
import json
from ctypes import wintypes
from dataclasses import dataclass

from core.powershell import PowerShellError, run_powershell

EMPTY_FLAGS = 0x00000001 | 0x00000002 | 0x00000004
CLEANUP_TIMEOUT_SECONDS = 600

BROWSER_PROCESSES = ("msedge", "chrome", "firefox")
UPDATE_SERVICES = ("wuauserv", "TrustedInstaller")

STATE_QUERY = r"""
$processes = @(Get-Process -Name msedge, chrome, firefox -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty ProcessName -Unique)
$services = @(Get-Service -Name wuauserv, TrustedInstaller -ErrorAction Stop |
    Where-Object { $_.Status -ne 'Stopped' } | Select-Object -ExpandProperty Name)
$delivery = [bool](Get-Command Delete-DeliveryOptimizationCache -ErrorAction SilentlyContinue)
ConvertTo-Json -Compress -InputObject @{ processes = $processes; services = $services; delivery = $delivery }
"""
DELIVERY_SIZE_QUERY = r"""
$size = (Get-DeliveryOptimizationStatus | Measure-Object -Property FileSizeInCache -Sum).Sum
Write-Output ([int64]$size)
"""
DELIVERY_CLEAR_COMMAND = "Delete-DeliveryOptimizationCache -Force -ErrorAction Stop"


class SHQUERYRBINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("i64Size", ctypes.c_longlong),
        ("i64NumItems", ctypes.c_longlong),
    ]


@dataclass(frozen=True)
class SystemState:
    running_processes: frozenset
    active_services: frozenset
    delivery_available: bool


def shell32():
    library = ctypes.WinDLL("shell32")
    library.SHQueryRecycleBinW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(SHQUERYRBINFO)]
    library.SHQueryRecycleBinW.restype = ctypes.c_long
    library.SHEmptyRecycleBinW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.DWORD]
    library.SHEmptyRecycleBinW.restype = ctypes.c_long
    return library


def read_recycle_bin():
    info = SHQUERYRBINFO(cbSize=ctypes.sizeof(SHQUERYRBINFO))
    if shell32().SHQueryRecycleBinW(None, ctypes.byref(info)) != 0:
        return 0, 0
    return info.i64Size, info.i64NumItems


def real_empty_recycle_bin():
    shell32().SHEmptyRecycleBinW(None, None, EMPTY_FLAGS)


def read_system_state(runner=run_powershell):
    try:
        data = json.loads(runner(STATE_QUERY))
        return SystemState(
            running_processes=frozenset(data["processes"]),
            active_services=frozenset(data["services"]),
            delivery_available=bool(data["delivery"]),
        )
    except (PowerShellError, ValueError, KeyError, TypeError):
        return SystemState(frozenset(BROWSER_PROCESSES), frozenset(UPDATE_SERVICES), False)


def read_delivery_size(runner=run_powershell):
    try:
        return max(int(runner(DELIVERY_SIZE_QUERY).strip() or 0), 0)
    except (PowerShellError, ValueError):
        return 0


def real_clear_delivery_optimization(runner=run_powershell):
    runner(DELIVERY_CLEAR_COMMAND, timeout=CLEANUP_TIMEOUT_SECONDS)
