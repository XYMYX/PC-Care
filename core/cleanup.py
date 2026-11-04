from dataclasses import dataclass, field

from core import activity_log, windows_cleanup
from core.categories import DELIVERY_OPTIMIZATION, FILES, RECYCLE_BIN, allowed_roots
from core.deletion import DeleteResult, delete_target, measure_target
from core.powershell import PowerShellError

READY = "ready"
EMPTY = "empty"
NOT_INSTALLED = "not_installed"
CLOSE_BROWSER = "close_browser"
NEEDS_ADMIN = "needs_admin"
OTHER_ACCOUNT = "other_account"
UPDATE_RUNNING = "update_running"
FAILED = "failed"

MEASURED_WHEN_BLOCKED = (CLOSE_BROWSER, UPDATE_RUNNING)


@dataclass(frozen=True)
class Preview:
    category: object
    status: str
    size: int = 0


@dataclass
class Outcome:
    category: object
    status: str
    result: DeleteResult = field(default_factory=DeleteResult)


def no_progress(_done, _total):
    return None


class Cleaner:
    def __init__(self, categories, is_admin, same_user=True, state_reader=None, log_folder=None):
        self.categories = categories
        self.is_admin = is_admin
        self.same_user = same_user
        self.state_reader = state_reader or windows_cleanup.read_system_state
        self.log_folder = log_folder
        self.roots = allowed_roots(categories)

    def blocker(self, category, state):
        if category.admin and not self.is_admin:
            return NEEDS_ADMIN
        if not category.admin and not self.same_user:
            return OTHER_ACCOUNT
        if not category.installed:
            return NOT_INSTALLED
        if category.kind == DELIVERY_OPTIMIZATION and not state.delivery_available:
            return NOT_INSTALLED
        if category.process in state.running_processes:
            return CLOSE_BROWSER
        if category.update_lock and state.active_services:
            return UPDATE_RUNNING
        return None

    def measure(self, category):
        if category.kind == RECYCLE_BIN:
            return windows_cleanup.read_recycle_bin()
        if category.kind == DELIVERY_OPTIMIZATION:
            size = windows_cleanup.read_delivery_size()
            return size, 1 if size else 0
        measurements = [measure_target(target) for target in category.targets]
        return sum(item.size for item in measurements), sum(item.files for item in measurements)

    def preview(self, report=no_progress):
        state = self.state_reader()
        previews = []
        for done, category in enumerate(self.categories):
            report(done, len(self.categories))
            blocked = self.blocker(category, state)
            if blocked is not None and blocked not in MEASURED_WHEN_BLOCKED:
                previews.append(Preview(category, blocked))
                continue
            size, items = self.measure(category)
            previews.append(Preview(category, blocked or (READY if items else EMPTY), size))
        report(len(self.categories), len(self.categories))
        return previews

    def clean_files(self, category):
        result = DeleteResult()
        for target in category.targets:
            result.add(delete_target(target, self.roots))
        return result

    def clean_recycle_bin(self):
        size_before, _items = windows_cleanup.read_recycle_bin()
        windows_cleanup.real_empty_recycle_bin()
        size_after, items_after = windows_cleanup.read_recycle_bin()
        return DeleteResult(deleted_bytes=max(size_before - size_after, 0), skipped_files=items_after)

    def clean_delivery_optimization(self):
        size_before = windows_cleanup.read_delivery_size()
        windows_cleanup.real_clear_delivery_optimization()
        size_after = windows_cleanup.read_delivery_size()
        return DeleteResult(deleted_bytes=max(size_before - size_after, 0))

    def clean_category(self, category):
        state = self.state_reader()
        blocked = self.blocker(category, state)
        if blocked is not None:
            activity_log.log_not_cleaned(category.key, blocked, self.log_folder)
            return Outcome(category, blocked)
        try:
            if category.kind == RECYCLE_BIN:
                result = self.clean_recycle_bin()
            elif category.kind == DELIVERY_OPTIMIZATION:
                result = self.clean_delivery_optimization()
            else:
                result = self.clean_files(category)
        except (PowerShellError, OSError) as error:
            activity_log.log_not_cleaned(category.key, str(error), self.log_folder)
            return Outcome(category, FAILED)
        for path in result.refused:
            activity_log.log_refused(category.key, path, self.log_folder)
        activity_log.log_cleanup(category.key, result.deleted_bytes, result.skipped_files, self.log_folder)
        return Outcome(category, READY, result)

    def clean(self, keys, report=no_progress):
        selected = [category for category in self.categories if category.key in keys]
        outcomes = []
        for done, category in enumerate(selected):
            report(done, len(selected))
            outcomes.append(self.clean_category(category))
        report(len(selected), len(selected))
        return outcomes


def total_freed(outcomes):
    return sum(outcome.result.deleted_bytes for outcome in outcomes)


def total_skipped(outcomes):
    return sum(outcome.result.skipped_files for outcome in outcomes)
