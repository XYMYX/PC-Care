from core.activity_log import LOG_FILE, MAX_LOG_BYTES, log_cleanup, trim_log


def test_small_log_is_left_alone(tmp_path):
    path = tmp_path / LOG_FILE
    path.write_bytes(b"line one\nline two\n")
    trim_log(path)
    assert path.read_bytes() == b"line one\nline two\n"


def test_missing_log_is_harmless(tmp_path):
    trim_log(tmp_path / LOG_FILE)
    assert not (tmp_path / LOG_FILE).exists()


def test_big_log_keeps_newest_whole_lines(tmp_path):
    path = tmp_path / LOG_FILE
    path.write_bytes(b"".join(b"entry %04d\n" % number for number in range(100)))
    trim_log(path, max_bytes=500, kept_bytes=105)
    lines = path.read_bytes().splitlines()
    assert lines[-1] == b"entry 0099"
    assert all(len(line) == 10 for line in lines)
    assert len(lines) == 9


def test_writing_keeps_the_log_small(tmp_path):
    path = tmp_path / LOG_FILE
    path.write_bytes(b"old entry\n" * (MAX_LOG_BYTES // 10 + 1))
    log_cleanup("thumbnails", 123, 0, tmp_path)
    assert path.stat().st_size < MAX_LOG_BYTES
    assert "deleted 123 bytes" in path.read_text(encoding="utf-8").splitlines()[-1]
