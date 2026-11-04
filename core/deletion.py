import fnmatch
import os
import stat
import time
from dataclasses import dataclass, field
from pathlib import Path

SECONDS_PER_HOUR = 3600
LINK_TAGS = (stat.IO_REPARSE_TAG_SYMLINK, stat.IO_REPARSE_TAG_MOUNT_POINT)

FILE = "file"
FOLDER = "folder"
LINK = "link"
BLOCKED = "blocked"
REFUSED = "refused"


@dataclass(frozen=True)
class Target:
    root: Path
    pattern: str | None = None
    min_age_hours: int = 0
    is_file: bool = False
    exclude: tuple = ()


@dataclass(frozen=True)
class Item:
    kind: str
    path: str
    info: os.stat_result | None = None


@dataclass
class Measurement:
    size: int = 0
    files: int = 0
    blocked: int = 0


@dataclass
class DeleteResult:
    deleted_bytes: int = 0
    deleted_files: int = 0
    skipped_files: int = 0
    refused: list = field(default_factory=list)

    def add(self, other):
        self.deleted_bytes += other.deleted_bytes
        self.deleted_files += other.deleted_files
        self.skipped_files += other.skipped_files
        self.refused.extend(other.refused)


def is_reparse(info):
    return bool(info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def is_link(info):
    return info.st_reparse_tag in LINK_TAGS


def is_recent(info, cutoff):
    return cutoff is not None and max(info.st_mtime, info.st_birthtime) > cutoff


def real_location(path):
    parent, name = os.path.split(os.path.abspath(path))
    return os.path.normcase(os.path.join(os.path.realpath(parent), name))


def is_inside(location, root):
    return location == root or location.startswith(root.rstrip(os.sep) + os.sep)


def is_allowed(path, allowed_roots):
    location = real_location(path)
    return any(is_inside(location, os.path.normcase(os.path.realpath(root))) for root in allowed_roots)


def walk(folder, target, cutoff, excluded):
    try:
        with os.scandir(folder) as scan:
            entries = list(scan)
    except FileNotFoundError:
        return
    except OSError:
        yield Item(BLOCKED, str(folder))
        return
    for entry in entries:
        path = entry.path
        if os.path.normcase(os.path.abspath(path)) in excluded:
            continue
        if target.pattern and not fnmatch.fnmatch(entry.name.lower(), target.pattern.lower()):
            continue
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            continue
        except OSError:
            yield Item(BLOCKED, path)
            continue
        if is_reparse(info):
            if not is_recent(info, cutoff):
                yield Item(LINK if is_link(info) else BLOCKED, path, info)
            continue
        if stat.S_ISDIR(info.st_mode):
            if target.pattern:
                continue
            yield from walk(path, target, cutoff, excluded)
            if not is_recent(info, cutoff):
                yield Item(FOLDER, path, info)
            continue
        if not is_recent(info, cutoff):
            yield Item(FILE, path, info)


def items_of(target, now):
    cutoff = None
    if target.min_age_hours:
        cutoff = now - target.min_age_hours * SECONDS_PER_HOUR
    try:
        info = os.lstat(target.root)
    except FileNotFoundError:
        return
    except OSError:
        yield Item(BLOCKED, str(target.root))
        return
    if is_reparse(info):
        yield Item(REFUSED, str(target.root))
        return
    if target.is_file:
        if not is_recent(info, cutoff):
            yield Item(FILE, str(target.root), info)
        return
    excluded = {os.path.normcase(os.path.abspath(path)) for path in target.exclude}
    yield from walk(target.root, target, cutoff, excluded)


def measure_target(target, now=None):
    measurement = Measurement()
    for item in items_of(target, now or time.time()):
        if item.kind == FILE:
            measurement.size += item.info.st_size
            measurement.files += 1
        elif item.kind == BLOCKED:
            measurement.blocked += 1
    return measurement


def remove_link(item):
    if item.info.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY:
        os.rmdir(item.path)
    else:
        os.unlink(item.path)


def delete_target(target, allowed_roots, now=None):
    result = DeleteResult()
    if not is_allowed(target.root, allowed_roots):
        result.refused.append(str(target.root))
        return result
    for item in items_of(target, now or time.time()):
        if item.kind == REFUSED or not is_allowed(item.path, allowed_roots):
            result.refused.append(item.path)
            continue
        if item.kind == BLOCKED:
            result.skipped_files += 1
            continue
        try:
            if item.kind == FILE:
                os.unlink(item.path)
                result.deleted_bytes += item.info.st_size
                result.deleted_files += 1
            elif item.kind == LINK:
                remove_link(item)
            else:
                os.rmdir(item.path)
        except FileNotFoundError:
            continue
        except OSError:
            if item.kind != FOLDER:
                result.skipped_files += 1
    return result
