import json

import pytest

from core import settings as settings_module
from core.settings import add_freed, format_size, load_settings, save_settings

MB = 1024 * 1024
GB = 1024 * MB


@pytest.fixture(autouse=True)
def german_windows(monkeypatch):
    monkeypatch.setattr(settings_module, "detect_language", lambda: "de")


def test_missing_file_uses_defaults(tmp_path):
    assert load_settings(tmp_path) == {"language": "de", "freed_bytes_total": 0}


@pytest.mark.parametrize("content", ["{broken", "", "[]", "null", "42", '"text"'])
def test_corrupt_file_uses_defaults(tmp_path, content):
    (tmp_path / "settings.json").write_text(content, encoding="utf-8")
    assert load_settings(tmp_path) == {"language": "de", "freed_bytes_total": 0}


def test_binary_file_uses_defaults(tmp_path):
    (tmp_path / "settings.json").write_bytes(b"\xff\xfe\x00\x80")
    assert load_settings(tmp_path) == {"language": "de", "freed_bytes_total": 0}


@pytest.mark.parametrize("total", [-1, "5", 1.5, None, True, [1]])
def test_invalid_total_is_ignored(tmp_path, total):
    data = {"language": "en", "freed_bytes_total": total}
    (tmp_path / "settings.json").write_text(json.dumps(data), encoding="utf-8")
    assert load_settings(tmp_path) == {"language": "en", "freed_bytes_total": 0}


def test_invalid_language_is_ignored(tmp_path):
    (tmp_path / "settings.json").write_text('{"language": "fr"}', encoding="utf-8")
    assert load_settings(tmp_path)["language"] == "de"


def test_counter_adds_up_and_is_saved(tmp_path):
    data = load_settings(tmp_path)
    add_freed(data, 2 * GB, tmp_path)
    add_freed(data, GB, tmp_path)
    assert load_settings(tmp_path)["freed_bytes_total"] == 3 * GB


def test_save_and_load(tmp_path):
    folder = tmp_path / "new" / "folder"
    data = {"language": "en", "freed_bytes_total": 12345}
    assert save_settings(data, folder)
    assert load_settings(folder) == data
    assert [path.name for path in folder.iterdir()] == ["settings.json"]


@pytest.mark.parametrize(
    ("size", "language", "expected"),
    [
        (0, "en", "0 MB"),
        (5 * MB, "de", "5 MB"),
        (1023 * MB, "en", "1023 MB"),
        (GB, "en", "1.0 GB"),
        (GB, "de", "1,0 GB"),
        (int(2.5 * GB), "de", "2,5 GB"),
        (int(2.5 * GB), "en", "2.5 GB"),
    ],
)
def test_format_size(size, language, expected):
    assert format_size(size, language) == expected
