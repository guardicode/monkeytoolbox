import pytest
from monkeytypes import OperatingSystem

from monkeytoolbox.environment import get_os


def test_get_os__linux(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert get_os() == OperatingSystem.LINUX


def test_get_os__windows(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert get_os() == OperatingSystem.WINDOWS


def test_get_os__unsupported(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    with pytest.raises(RuntimeError):
        get_os()
