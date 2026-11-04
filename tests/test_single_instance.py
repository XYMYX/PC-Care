import threading
import time
import uuid

import pytest

from core import single_instance
from core.single_instance import acquire, release


@pytest.fixture
def name():
    return f"Local\\XYMYX-PC-Care-Test-{uuid.uuid4()}"


def test_first_start_gets_the_lock(name):
    handle = acquire(name)
    assert handle
    release(handle)


def test_second_start_is_refused(name):
    first = acquire(name)
    assert acquire(name) is None
    release(first)


def test_lock_is_free_after_release(name):
    release(acquire(name))
    handle = acquire(name)
    assert handle
    release(handle)


def test_restart_waits_for_the_old_window(name):
    first = acquire(name)
    timer = threading.Timer(0.3, release, [first])
    timer.start()
    started = time.monotonic()
    handle = acquire(name, wait_seconds=5)
    assert handle
    assert 0.2 < time.monotonic() - started < 3
    release(handle)
    timer.join()


def test_restart_gives_up_after_waiting(name):
    first = acquire(name)
    assert acquire(name, wait_seconds=0.3) is None
    release(first)


def test_no_window_found_is_harmless():
    assert single_instance.show_running_window(f"No such window {uuid.uuid4()}") is False
