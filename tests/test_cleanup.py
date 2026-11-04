from pathlib import Path

import pytest

from core import windows_cleanup
from core.activity_log import LOG_FILE
from core.categories import SystemPaths, allowed_roots, build_categories, is_safe_temp
from core.cleanup import (
    CLOSE_BROWSER,
    EMPTY,
    FAILED,
    NEEDS_ADMIN,
    NOT_INSTALLED,
    OTHER_ACCOUNT,
    READY,
    UPDATE_RUNNING,
    Cleaner,
    total_freed,
    total_skipped,
)
from core.deletion import measure_target
from core.powershell import PowerShellError
from core.windows_cleanup import SystemState, read_system_state

LATER = 10**11


@pytest.fixture
def paths(tmp_path):
    local = tmp_path / "local"
    temp = local / "Temp"
    windows = tmp_path / "windows"
    temp.mkdir(parents=True)
    windows.mkdir()
    return SystemPaths(local, temp, windows)


@pytest.fixture(autouse=True)
def fake_system_readers(monkeypatch):
    monkeypatch.setattr(windows_cleanup, "read_recycle_bin", lambda: (0, 0))
    monkeypatch.setattr(windows_cleanup, "read_delivery_size", lambda: 0)


def write(path, size=10):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    return path


def state(processes=(), services=(), delivery=True):
    return SystemState(frozenset(processes), frozenset(services), delivery)


def cleaner(paths, tmp_path, is_admin=False, same_user=True, current=None):
    return Cleaner(
        build_categories(paths),
        is_admin,
        same_user,
        state_reader=lambda: current or state(),
        log_folder=tmp_path / "log",
    )


def statuses(tool):
    return {preview.category.key: preview.status for preview in tool.preview()}


def sizes(tool):
    return {preview.category.key: preview.size for preview in tool.preview()}


def log_text(tmp_path):
    return (tmp_path / "log" / LOG_FILE).read_text(encoding="utf-8")


def test_all_listed_categories_exist(paths):
    keys = {category.key for category in build_categories(paths)}
    assert keys == {
        "user_temp", "edge", "chrome", "firefox", "recycle_bin", "thumbnails",
        "directx_shader", "gpu_shader", "error_reports", "windows_temp",
        "windows_update", "windows_logs", "crash_dumps", "delivery_optimization",
    }


def test_admin_categories_are_marked(paths):
    admin = {category.key for category in build_categories(paths) if category.admin}
    assert admin == {
        "windows_temp", "windows_update", "windows_logs", "crash_dumps", "delivery_optimization",
    }


@pytest.mark.parametrize(
    "forbidden", ["prefetch", "winsxs", "windows.old", "hiberfil", "pagefile", "system32"]
)
def test_allowlist_never_lists_protected_places(forbidden):
    paths = SystemPaths(Path("C:/L"), Path("C:/L/Temp"), Path("C:/Windows"))
    for root in allowed_roots(build_categories(paths)):
        assert forbidden not in str(root).lower()


def test_windows_folder_itself_is_never_a_root():
    paths = SystemPaths(Path("C:/L"), Path("C:/L/Temp"), Path("C:/Windows"))
    roots = allowed_roots(build_categories(paths))
    assert Path("C:/Windows") not in roots
    assert Path("C:/Windows/MEMORY.DMP") in roots


def test_browser_targets_are_only_cache_folders(paths):
    data = paths.local / "Google" / "Chrome" / "User Data"
    (data / "Default").mkdir(parents=True)
    (data / "Profile 2").mkdir()
    (data / "Crashpad").mkdir()
    chrome = next(category for category in build_categories(paths) if category.key == "chrome")
    names = {target.root.name for target in chrome.targets}
    parents = {target.root.parent.name for target in chrome.targets}
    assert names == {
        "Cache", "Code Cache", "GPUCache", "DawnWebGPUCache", "DawnGraphiteCache",
        "ShaderCache", "GrShaderCache", "GraphiteDawnCache",
    }
    assert parents == {"User Data", "Default", "Profile 2"}


def test_browser_cleanup_keeps_personal_data(paths, tmp_path):
    profile = paths.local / "Google" / "Chrome" / "User Data" / "Default"
    write(profile / "Cache" / "Cache_Data" / "data_0", 100)
    write(profile / "Code Cache" / "js" / "index", 50)
    personal = [
        write(profile / name)
        for name in (
            "Cookies", "History", "Login Data", "Bookmarks", "Preferences",
            "Sessions/Session_1", "Extensions/abc/manifest.json",
        )
    ]
    tool = cleaner(paths, tmp_path)
    assert statuses(tool)["chrome"] == READY
    outcomes = tool.clean({"chrome"})
    assert total_freed(outcomes) == 150
    assert all(path.exists() for path in personal)
    assert (profile / "Cache").is_dir()


def test_firefox_cache_keeps_personal_data(paths, tmp_path):
    profile = paths.local / "Mozilla" / "Firefox" / "Profiles" / "abc.default-release"
    write(profile / "cache2" / "entries" / "ABC", 70)
    write(profile / "startupCache" / "scriptCache.bin", 30)
    kept = write(profile / "jumpListCache" / "x.ico")
    tool = cleaner(paths, tmp_path)
    assert total_freed(tool.clean({"firefox"})) == 100
    assert kept.exists()


def test_missing_software_is_unavailable(paths, tmp_path):
    result = statuses(cleaner(paths, tmp_path))
    assert result["edge"] == result["chrome"] == result["firefox"] == NOT_INSTALLED


def test_nothing_to_clean_is_unavailable(paths, tmp_path):
    result = statuses(cleaner(paths, tmp_path))
    assert result["directx_shader"] == EMPTY
    assert result["error_reports"] == EMPTY
    assert result["recycle_bin"] == EMPTY


@pytest.mark.parametrize(
    ("process", "key", "cache"),
    [
        ("msedge", "edge", "Microsoft/Edge/User Data/Default/Cache/x"),
        ("chrome", "chrome", "Google/Chrome/User Data/Default/Cache/x"),
        ("firefox", "firefox", "Mozilla/Firefox/Profiles/a/cache2/x"),
    ],
)
def test_running_browser_is_blocked_and_untouched(paths, tmp_path, process, key, cache):
    cached = write(paths.local / cache)
    tool = cleaner(paths, tmp_path, current=state([process]))
    assert statuses(tool)[key] == CLOSE_BROWSER
    assert tool.clean({key})[0].status == CLOSE_BROWSER
    assert cached.exists()


def test_browser_started_after_preview_is_still_protected(paths, tmp_path):
    cache = write(paths.local / "Google" / "Chrome" / "User Data" / "Default" / "Cache" / "x")
    answers = iter([state(), state(["chrome"])])
    tool = Cleaner(
        build_categories(paths), False, state_reader=lambda: next(answers), log_folder=tmp_path
    )
    assert statuses(tool)["chrome"] == READY
    assert tool.clean({"chrome"})[0].status == CLOSE_BROWSER
    assert cache.exists()


def test_webview_does_not_count_as_edge():
    assert "msedgewebview2" not in windows_cleanup.STATE_QUERY
    assert "msedgewebview2" not in windows_cleanup.BROWSER_PROCESSES


def test_failed_state_query_blocks_instead_of_guessing():
    def failing(_query):
        raise PowerShellError("no")

    current = read_system_state(failing)
    assert "chrome" in current.running_processes
    assert "wuauserv" in current.active_services
    assert current.delivery_available is False


def test_state_query_parsing():
    output = '{"processes":["chrome"],"services":[],"delivery":true}'
    assert read_system_state(lambda _query: output) == state(["chrome"], [], True)


def test_admin_categories_need_admin(paths, tmp_path):
    dump = write(paths.windows / "Minidump" / "a.dmp")
    tool = cleaner(paths, tmp_path, is_admin=False)
    assert statuses(tool)["crash_dumps"] == NEEDS_ADMIN
    assert tool.clean({"crash_dumps"})[0].status == NEEDS_ADMIN
    assert dump.exists()


def test_admin_mode_cleans_dummy_windows_folders(paths, tmp_path):
    write(paths.windows / "Minidump" / "a.dmp", 20)
    write(paths.windows / "MEMORY.DMP", 30)
    write(paths.windows / "Logs" / "CBS" / "CBS.log", 40)
    kept = write(paths.windows / "explorer.exe")
    tool = cleaner(paths, tmp_path, is_admin=True)
    assert total_freed(tool.clean({"crash_dumps", "windows_logs"})) == 90
    assert kept.exists()
    assert (paths.windows / "Logs").is_dir()
    assert (paths.windows / "Minidump").is_dir()


@pytest.mark.parametrize("service", ["wuauserv", "TrustedInstaller"])
def test_update_cache_waits_for_update_services(paths, tmp_path, service):
    download = write(paths.windows / "SoftwareDistribution" / "Download" / "update.cab")
    tool = cleaner(paths, tmp_path, is_admin=True, current=state(services=[service]))
    assert statuses(tool)["windows_update"] == UPDATE_RUNNING
    assert tool.clean({"windows_update"})[0].status == UPDATE_RUNNING
    assert download.exists()


def test_update_cache_is_cleaned_when_services_stopped(paths, tmp_path):
    write(paths.windows / "SoftwareDistribution" / "Download" / "update.cab", 50)
    tool = cleaner(paths, tmp_path, is_admin=True)
    assert total_freed(tool.clean({"windows_update"})) == 50


def test_other_account_hides_personal_categories(paths, tmp_path):
    temp_file = write(paths.temp / "old.tmp")
    tool = cleaner(paths, tmp_path, is_admin=True, same_user=False)
    assert statuses(tool)["user_temp"] == OTHER_ACCOUNT
    assert tool.clean({"user_temp"})[0].status == OTHER_ACCOUNT
    assert temp_file.exists()


def test_temp_keeps_recent_files_in_preview(paths):
    write(paths.temp / "new.tmp", 10)
    category = build_categories(paths)[0]
    assert measure_target(category.targets[0]).size == 0
    assert measure_target(category.targets[0], now=LATER).size == 10


def test_thumbnails_only_touch_thumbcache(paths, tmp_path):
    explorer = paths.local / "Microsoft" / "Windows" / "Explorer"
    write(explorer / "thumbcache_32.db", 11)
    icon = write(explorer / "iconcache_32.db")
    tool = cleaner(paths, tmp_path)
    assert sizes(tool)["thumbnails"] == 11
    assert total_freed(tool.clean({"thumbnails"})) == 11
    assert icon.exists()


def test_locked_thumbnail_is_skipped(paths, tmp_path):
    locked = write(paths.local / "Microsoft" / "Windows" / "Explorer" / "thumbcache_32.db")
    tool = cleaner(paths, tmp_path)
    with open(locked, "rb"):
        outcomes = tool.clean({"thumbnails"})
    assert total_skipped(outcomes) == 1
    assert total_freed(outcomes) == 0
    assert locked.exists()


def test_freed_space_is_real_bytes_not_the_estimate(paths, tmp_path):
    locked = write(paths.local / "D3DSCache" / "locked.bin", 1000)
    write(paths.local / "D3DSCache" / "free.bin", 24)
    tool = cleaner(paths, tmp_path)
    assert sizes(tool)["directx_shader"] == 1024
    with open(locked, "rb"):
        outcomes = tool.clean({"directx_shader"})
    assert total_freed(outcomes) == 24
    assert total_skipped(outcomes) == 1


def test_only_selected_categories_are_cleaned(paths, tmp_path):
    chosen = write(paths.local / "D3DSCache" / "a.bin")
    other = write(paths.local / "NVIDIA" / "DXCache" / "b.nvph")
    cleaner(paths, tmp_path).clean({"directx_shader"})
    assert not chosen.exists()
    assert other.exists()


def test_nothing_selected_deletes_nothing(paths, tmp_path):
    kept = write(paths.local / "D3DSCache" / "a.bin")
    assert cleaner(paths, tmp_path).clean(set()) == []
    assert kept.exists()


def test_preview_deletes_nothing(paths, tmp_path):
    kept = write(paths.local / "D3DSCache" / "a.bin")
    cleaner(paths, tmp_path).preview()
    assert kept.exists()


def test_recycle_bin_uses_api_and_counts_real_bytes(paths, tmp_path, monkeypatch):
    levels = iter([(100, 3), (30, 1)])
    calls = []
    monkeypatch.setattr(windows_cleanup, "read_recycle_bin", lambda: next(levels))
    monkeypatch.setattr(windows_cleanup, "real_empty_recycle_bin", lambda: calls.append("empty"))
    outcomes = cleaner(paths, tmp_path).clean({"recycle_bin"})
    assert calls == ["empty"]
    assert total_freed(outcomes) == 70
    assert total_skipped(outcomes) == 1


def test_delivery_optimization_uses_cmdlet_and_counts_real_bytes(paths, tmp_path, monkeypatch):
    levels = iter([500, 100])
    calls = []
    monkeypatch.setattr(windows_cleanup, "read_delivery_size", lambda: next(levels))
    monkeypatch.setattr(
        windows_cleanup, "real_clear_delivery_optimization", lambda: calls.append("clear")
    )
    outcomes = cleaner(paths, tmp_path, is_admin=True).clean({"delivery_optimization"})
    assert calls == ["clear"]
    assert total_freed(outcomes) == 400


def test_delivery_optimization_without_cmdlet_is_unavailable(paths, tmp_path):
    tool = cleaner(paths, tmp_path, is_admin=True, current=state(delivery=False))
    assert statuses(tool)["delivery_optimization"] == NOT_INSTALLED


def test_delivery_optimization_failure_is_reported(paths, tmp_path, monkeypatch):
    def failing():
        raise PowerShellError("denied")

    monkeypatch.setattr(windows_cleanup, "real_clear_delivery_optimization", failing)
    outcome = cleaner(paths, tmp_path, is_admin=True).clean({"delivery_optimization"})[0]
    assert outcome.status == FAILED
    assert "denied" in log_text(tmp_path)


def test_every_cleanup_is_logged(paths, tmp_path):
    write(paths.local / "D3DSCache" / "a.bin", 123)
    cleaner(paths, tmp_path).clean({"directx_shader"})
    line = log_text(tmp_path).strip()
    assert "directx_shader" in line
    assert "deleted 123 bytes" in line
    assert "skipped 0 files" in line
    assert line[:4].isdigit()


def test_refused_paths_are_logged(paths, tmp_path):
    kept = write(paths.local / "D3DSCache" / "a.bin")
    tool = cleaner(paths, tmp_path)
    tool.roots = [tmp_path / "somewhere-else"]
    outcome = tool.clean({"directx_shader"})[0]
    assert outcome.result.refused
    assert "REFUSED" in log_text(tmp_path)
    assert kept.exists()


def test_progress_is_reported(paths, tmp_path):
    seen = []
    cleaner(paths, tmp_path).preview(lambda done, total: seen.append((done, total)))
    assert seen[0] == (0, 14)
    assert seen[-1] == (14, 14)


@pytest.mark.parametrize(
    ("temp", "safe"),
    [
        ("C:/Users/A/AppData/Local/Temp", True),
        ("D:/Temp", True),
        ("D:/tmp", True),
        ("C:/", False),
        ("D:/Games", False),
        ("C:/Users/A", False),
        ("C:/Windows", False),
        ("C:/Windows/Temp", False),
        ("C:/Windows/System32/tmp", False),
    ],
)
def test_broken_temp_setting_is_rejected(temp, safe):
    assert is_safe_temp(Path(temp), Path("C:/Windows")) is safe


def test_broken_temp_setting_gives_no_target(tmp_path):
    paths = SystemPaths(tmp_path, tmp_path / "Documents", tmp_path / "windows")
    assert build_categories(paths)[0].targets == ()
