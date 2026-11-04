import _winapi
import os
import time

import pytest

from core.deletion import Target, delete_target, measure_target

DAY = 24 * 3600


@pytest.fixture
def root(tmp_path):
    folder = tmp_path / "allowed"
    folder.mkdir()
    return folder


@pytest.fixture
def outside(tmp_path):
    folder = tmp_path / "outside"
    folder.mkdir()
    (folder / "keep.txt").write_text("precious")
    return folder


def write(path, size=10):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    return path


def test_deletes_contents_but_keeps_root(root):
    write(root / "a.tmp", 100)
    write(root / "sub" / "deep" / "b.tmp", 50)
    result = delete_target(Target(root), [root])
    assert result.deleted_bytes == 150
    assert result.deleted_files == 2
    assert result.skipped_files == 0
    assert root.is_dir()
    assert list(root.iterdir()) == []


def test_empty_folder(root):
    (root / "empty").mkdir()
    result = delete_target(Target(root), [root])
    assert result.deleted_bytes == 0
    assert result.skipped_files == 0
    assert list(root.iterdir()) == []


def test_empty_root_stays(root):
    assert delete_target(Target(root), [root]).deleted_files == 0
    assert root.is_dir()


def test_missing_root_is_harmless(root):
    missing = root / "missing"
    assert delete_target(Target(missing), [root]).deleted_files == 0


def test_root_outside_allowlist_is_refused(root, outside):
    result = delete_target(Target(outside), [root])
    assert result.refused == [str(outside)]
    assert result.deleted_files == 0
    assert (outside / "keep.txt").exists()


def test_similar_folder_name_is_not_inside(root, tmp_path):
    sibling = tmp_path / "allowed-but-not-really"
    write(sibling / "keep.txt")
    result = delete_target(Target(sibling), [root])
    assert result.refused
    assert (sibling / "keep.txt").exists()


def test_parent_traversal_is_refused(root, outside):
    result = delete_target(Target(root / ".." / "outside"), [root])
    assert result.refused
    assert (outside / "keep.txt").exists()


def test_junction_inside_root_removes_only_the_link(root, outside):
    write(root / "a.tmp")
    link = root / "link"
    _winapi.CreateJunction(str(outside), str(link))
    result = delete_target(Target(root), [root])
    assert (outside / "keep.txt").read_text() == "precious"
    assert not os.path.lexists(link)
    assert result.deleted_files == 1
    assert result.deleted_bytes == 10


def test_nested_junction_is_not_followed(root, outside):
    (root / "sub").mkdir()
    _winapi.CreateJunction(str(outside), str(root / "sub" / "link"))
    delete_target(Target(root), [root])
    assert (outside / "keep.txt").exists()


def test_other_reparse_points_are_skipped_not_removed(root, outside, monkeypatch):
    from core import deletion

    link = root / "cloud-file"
    _winapi.CreateJunction(str(outside), str(link))
    monkeypatch.setattr(deletion, "is_link", lambda _info: False)
    result = delete_target(Target(root), [root])
    assert result.skipped_files == 1
    assert os.path.lexists(link)
    assert (outside / "keep.txt").exists()


def test_junction_as_root_is_refused(root, outside):
    link = root / "link"
    _winapi.CreateJunction(str(outside), str(link))
    result = delete_target(Target(link), [root])
    assert result.refused == [str(link)]
    assert (outside / "keep.txt").exists()
    assert os.path.lexists(link)


def test_junction_as_root_is_refused_even_if_allowlisted(root, outside):
    link = root / "link"
    _winapi.CreateJunction(str(outside), str(link))
    result = delete_target(Target(link), [link])
    assert result.refused
    assert (outside / "keep.txt").exists()


def test_junction_is_not_measured(root, outside):
    write(root / "a.tmp", 10)
    _winapi.CreateJunction(str(outside), str(root / "link"))
    measurement = measure_target(Target(root))
    assert measurement.size == 10
    assert measurement.files == 1


def test_symlink_removes_only_the_link(root, outside):
    link = root / "link.txt"
    try:
        os.symlink(outside / "keep.txt", link)
    except OSError:
        pytest.skip("Creating symlinks needs Developer Mode or admin rights")
    delete_target(Target(root), [root])
    assert not os.path.lexists(link)
    assert (outside / "keep.txt").read_text() == "precious"


def test_locked_file_is_skipped_and_counted(root):
    locked = write(root / "locked.tmp", 100)
    write(root / "free.tmp", 40)
    with open(locked, "rb"):
        result = delete_target(Target(root), [root])
    assert result.skipped_files == 1
    assert result.deleted_files == 1
    assert result.deleted_bytes == 40
    assert locked.exists()


def test_locked_file_keeps_its_folder(root):
    locked = write(root / "sub" / "locked.tmp")
    with open(locked, "rb"):
        result = delete_target(Target(root), [root])
    assert result.skipped_files == 1
    assert locked.exists()


def test_read_only_file_is_skipped_and_counted(root):
    protected = write(root / "protected.tmp")
    os.chmod(protected, 0o444)
    try:
        result = delete_target(Target(root), [root])
        assert result.skipped_files == 1
        assert protected.exists()
    finally:
        os.chmod(protected, 0o666)


def test_recent_files_are_kept(root):
    write(root / "new.tmp", 10)
    result = delete_target(Target(root, min_age_hours=24), [root])
    assert result.deleted_files == 0
    assert (root / "new.tmp").exists()


def test_old_files_are_deleted_with_age_rule(root):
    write(root / "sub" / "old.tmp", 10)
    later = time.time() + 2 * DAY
    assert measure_target(Target(root, min_age_hours=24), now=later).size == 10
    result = delete_target(Target(root, min_age_hours=24), [root], now=later)
    assert result.deleted_files == 1
    assert list(root.iterdir()) == []


def test_old_change_date_on_new_file_is_still_recent(root):
    extracted = write(root / "setup.exe", 10)
    old = time.time() - 30 * DAY
    os.utime(extracted, (old, old))
    assert delete_target(Target(root, min_age_hours=24), [root]).deleted_files == 0
    assert extracted.exists()


def test_recently_changed_file_is_kept_after_a_day(root):
    changed = write(root / "changed.tmp", 10)
    later = time.time() + 2 * DAY
    os.utime(changed, (later, later))
    target = Target(root, min_age_hours=24)
    assert delete_target(target, [root], now=later).deleted_files == 0


def test_pattern_matches_only_top_level_names(root):
    write(root / "thumbcache_32.db")
    write(root / "THUMBCACHE_96.DB")
    write(root / "iconcache_32.db")
    write(root / "sub" / "thumbcache_16.db")
    result = delete_target(Target(root, pattern="thumbcache_*.db"), [root])
    assert result.deleted_files == 2
    assert (root / "iconcache_32.db").exists()
    assert (root / "sub" / "thumbcache_16.db").exists()


def test_single_file_target(root):
    dump = write(root / "MEMORY.DMP", 30)
    other = write(root / "system.dat")
    result = delete_target(Target(dump, is_file=True), [dump])
    assert result.deleted_bytes == 30
    assert not dump.exists()
    assert other.exists()


def test_single_file_allowlist_does_not_open_the_folder(root):
    dump = write(root / "MEMORY.DMP")
    other = write(root / "system.dat")
    result = delete_target(Target(other, is_file=True), [dump])
    assert result.refused
    assert other.exists()


def test_excluded_folder_is_left_alone(root):
    running = write(root / "_MEI123" / "app.dll")
    write(root / "other.tmp")
    target = Target(root, exclude=(running.parent,))
    assert measure_target(target).files == 1
    assert delete_target(target, [root]).deleted_files == 1
    assert running.exists()


def test_measure_deletes_nothing(root):
    write(root / "a.tmp", 25)
    write(root / "sub" / "b.tmp", 5)
    measurement = measure_target(Target(root))
    assert measurement.size == 30
    assert measurement.files == 2
    assert (root / "a.tmp").exists()
    assert (root / "sub" / "b.tmp").exists()


def test_folder_swapped_for_junction_during_cleanup_is_refused(root, outside, monkeypatch):
    from core import deletion

    planned = write(root / "sub" / "a.tmp")

    def swapping_walk(_folder, _target, _cutoff, _excluded):
        info = os.lstat(planned)
        os.unlink(planned)
        os.rmdir(root / "sub")
        _winapi.CreateJunction(str(outside), str(root / "sub"))
        yield deletion.Item(deletion.FILE, str(root / "sub" / "keep.txt"), info)

    monkeypatch.setattr(deletion, "walk", swapping_walk)
    result = delete_target(Target(root), [root])
    assert result.refused
    assert (outside / "keep.txt").exists()
