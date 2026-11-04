import ctypes
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from core.deletion import Target

FILES = "files"
RECYCLE_BIN = "recycle_bin"
DELIVERY_OPTIMIZATION = "delivery_optimization"

TEMP_AGE_HOURS = 24

CHROMIUM_PROFILE = re.compile(r"^(Default|Guest Profile|Profile \d+)$")
CHROMIUM_PROFILE_CACHES = ("Cache", "Code Cache", "GPUCache", "DawnWebGPUCache", "DawnGraphiteCache")
CHROMIUM_SHARED_CACHES = ("ShaderCache", "GrShaderCache", "GraphiteDawnCache")
FIREFOX_CACHES = ("cache2", "startupCache")
GPU_CACHES = (("NVIDIA", "DXCache"), ("NVIDIA", "GLCache"), ("AMD", "DxCache"), ("AMD", "GLCache"))
ERROR_REPORT_FOLDERS = ("ReportArchive", "ReportQueue", "Temp")
BROWSER_NAMES = {"msedge": "Edge", "chrome": "Chrome", "firefox": "Firefox"}


@dataclass(frozen=True)
class SystemPaths:
    local: Path
    temp: Path
    windows: Path


@dataclass(frozen=True)
class Category:
    key: str
    targets: tuple = ()
    admin: bool = False
    kind: str = FILES
    process: str | None = None
    installed: bool = True
    update_lock: bool = False


def windows_folder():
    buffer = ctypes.create_unicode_buffer(260)
    ctypes.windll.kernel32.GetWindowsDirectoryW(buffer, len(buffer))
    return Path(buffer.value)


def system_paths():
    local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    temp = os.environ.get("TEMP") or str(Path(local) / "Temp")
    return SystemPaths(Path(local), Path(temp), windows_folder())


def runtime_exclusions():
    running_from = getattr(sys, "_MEIPASS", None)
    return (Path(running_from),) if running_from else ()


def is_safe_temp(temp, windows):
    name = temp.name.lower()
    if "temp" not in name and "tmp" not in name:
        return False
    folder = os.path.normcase(os.path.abspath(temp))
    system_root = os.path.normcase(os.path.abspath(windows))
    return not (folder == system_root or folder.startswith(system_root + os.sep))


def chromium_targets(user_data):
    targets = [user_data / name for name in CHROMIUM_SHARED_CACHES]
    try:
        with os.scandir(user_data) as entries:
            profiles = [entry.name for entry in entries if CHROMIUM_PROFILE.match(entry.name)]
    except OSError:
        profiles = []
    for profile in sorted(profiles):
        targets.extend(user_data / profile / name for name in CHROMIUM_PROFILE_CACHES)
    return tuple(Target(path) for path in targets)


def firefox_targets(profiles):
    try:
        with os.scandir(profiles) as entries:
            names = sorted(entry.name for entry in entries)
    except OSError:
        return ()
    return tuple(Target(profiles / name / cache) for name in names for cache in FIREFOX_CACHES)


def build_categories(paths, exclude=()):
    local = paths.local
    windows = paths.windows
    edge_data = local / "Microsoft" / "Edge" / "User Data"
    chrome_data = local / "Google" / "Chrome" / "User Data"
    firefox_profiles = local / "Mozilla" / "Firefox" / "Profiles"
    error_reports = local / "Microsoft" / "Windows" / "WER"
    temp_targets = ()
    if is_safe_temp(paths.temp, windows):
        temp_targets = (Target(paths.temp, min_age_hours=TEMP_AGE_HOURS, exclude=exclude),)
    return (
        Category("user_temp", temp_targets),
        Category("edge", chromium_targets(edge_data), process="msedge", installed=edge_data.is_dir()),
        Category("chrome", chromium_targets(chrome_data), process="chrome", installed=chrome_data.is_dir()),
        Category(
            "firefox",
            firefox_targets(firefox_profiles),
            process="firefox",
            installed=firefox_profiles.is_dir(),
        ),
        Category("recycle_bin", kind=RECYCLE_BIN),
        Category(
            "thumbnails",
            (Target(local / "Microsoft" / "Windows" / "Explorer", pattern="thumbcache_*.db"),),
        ),
        Category("directx_shader", (Target(local / "D3DSCache"),)),
        Category("gpu_shader", tuple(Target(local / vendor / name) for vendor, name in GPU_CACHES)),
        Category("error_reports", tuple(Target(error_reports / name) for name in ERROR_REPORT_FOLDERS)),
        Category(
            "windows_temp",
            (Target(windows / "Temp", min_age_hours=TEMP_AGE_HOURS),),
            admin=True,
        ),
        Category(
            "windows_update",
            (Target(windows / "SoftwareDistribution" / "Download"),),
            admin=True,
            update_lock=True,
        ),
        Category("windows_logs", (Target(windows / "Logs"),), admin=True),
        Category(
            "crash_dumps",
            (Target(windows / "Minidump"), Target(windows / "MEMORY.DMP", is_file=True)),
            admin=True,
        ),
        Category("delivery_optimization", admin=True, kind=DELIVERY_OPTIMIZATION),
    )


def allowed_roots(categories):
    return [target.root for category in categories for target in category.targets]
