import pytest
from monkeytoolbox import get_os
from monkeytypes import OperatingSystem

@pytest.fixture
def home_env_variable():
    if get_os() == OperatingSystem.WINDOWS:
        return "%USERPROFILE%"
    else:
        return "$HOME"

@pytest.fixture
def patched_home_env(monkeypatch, tmp_path, home_env_variable):
    monkeypatch.setenv(home_env_variable.strip("%$"), str(tmp_path))

    return tmp_path
