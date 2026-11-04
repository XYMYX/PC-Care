import pytest


class ForbiddenCall(Exception):
    pass


def forbidden(*_args, **_kwargs):
    raise ForbiddenCall("A test tried to reach the real system")


@pytest.fixture(autouse=True)
def block_real_system_cleanup(monkeypatch):
    from core import windows_cleanup

    monkeypatch.setattr(windows_cleanup, "real_empty_recycle_bin", forbidden)
    monkeypatch.setattr(windows_cleanup, "real_clear_delivery_optimization", forbidden)
