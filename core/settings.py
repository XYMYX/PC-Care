import ctypes
import json
import os
from pathlib import Path

from core.texts import LANGUAGES

APP_FOLDER = "XYMYX PC Care"
SETTINGS_FILE = "settings.json"
GERMAN_LANGUAGE_ID = 0x07
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * BYTES_PER_MB


def app_data_dir():
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / APP_FOLDER


def detect_language():
    language_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    return "de" if language_id & 0x3FF == GERMAN_LANGUAGE_ID else "en"


def default_settings():
    return {"language": detect_language(), "freed_bytes_total": 0}


def load_settings(folder=None):
    settings = default_settings()
    path = Path(folder or app_data_dir()) / SETTINGS_FILE
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return settings
    if not isinstance(stored, dict):
        return settings
    if stored.get("language") in LANGUAGES:
        settings["language"] = stored["language"]
    total = stored.get("freed_bytes_total")
    if type(total) is int and total >= 0:
        settings["freed_bytes_total"] = total
    return settings


def save_settings(settings, folder=None):
    target = Path(folder or app_data_dir())
    temporary = target / f"{SETTINGS_FILE}.tmp"
    try:
        target.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        os.replace(temporary, target / SETTINGS_FILE)
    except OSError:
        return False
    return True


def add_freed(settings, freed_bytes, folder=None):
    settings["freed_bytes_total"] += freed_bytes
    return save_settings(settings, folder)


def format_size(size_bytes, language):
    if size_bytes >= BYTES_PER_GB:
        value = f"{size_bytes / BYTES_PER_GB:.1f}"
        if language == "de":
            value = value.replace(".", ",")
        return f"{value} GB"
    return f"{size_bytes / BYTES_PER_MB:.0f} MB"
