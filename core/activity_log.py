from datetime import datetime
from pathlib import Path

from core.settings import app_data_dir

LOG_FILE = "log.txt"


def write_line(message, folder=None):
    target = Path(folder or app_data_dir())
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        target.mkdir(parents=True, exist_ok=True)
        with open(target / LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"{stamp} | {message}\n")
    except OSError:
        return False
    return True


def log_cleanup(category, deleted_bytes, skipped_files, folder=None):
    return write_line(f"{category} | deleted {deleted_bytes} bytes | skipped {skipped_files} files", folder)


def log_refused(category, path, folder=None):
    return write_line(f"{category} | REFUSED outside allowlist or link: {path}", folder)


def log_not_cleaned(category, reason, folder=None):
    return write_line(f"{category} | not cleaned: {reason}", folder)
