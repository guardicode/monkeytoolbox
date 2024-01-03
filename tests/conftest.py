import pytest
from monkeytoolbox import is_windows_os

@pytest.fixture
def home_env_variable():
    if is_windows_os():
        return "%USERPROFILE%"
    else:
        return "$HOME"

@pytest.fixture
def patched_home_env(monkeypatch, tmp_path, home_env_variable):
    monkeypatch.setenv(home_env_variable.strip("%$"), str(tmp_path))

    return tmp_path
