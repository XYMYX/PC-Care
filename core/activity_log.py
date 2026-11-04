from datetime import datetime
from pathlib import Path

from core.settings import app_data_dir

LOG_FILE = "log.txt"
MAX_LOG_BYTES = 1024 * 1024
KEPT_LOG_BYTES = MAX_LOG_BYTES // 2


def trim_log(path, max_bytes=MAX_LOG_BYTES, kept_bytes=KEPT_LOG_BYTES):
    if not path.exists() or path.stat().st_size <= max_bytes:
        return
    content = path.read_bytes()[-kept_bytes:]
    path.write_bytes(content[content.find(b"\n") + 1:])


def write_line(message, folder=None):
    target = Path(folder or app_data_dir())
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        target.mkdir(parents=True, exist_ok=True)
        trim_log(target / LOG_FILE)
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
