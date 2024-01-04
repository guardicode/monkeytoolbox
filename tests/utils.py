from pathlib import Path, PosixPath, WindowsPath
from typing import Iterable

from monkeytypes import OperatingSystem

from monkeytoolbox import get_os

if get_os() == OperatingSystem.WINDOWS:
    import win32api
    import win32security

    import monkeytoolbox.windows_permissions as windows_permissions
else:
    import os
    import stat


def assert_windows_permissions(path: WindowsPath):
    acl, user_sid = _get_acl_and_sid_from_path(path)

    assert acl.GetAceCount() == 1

    ace = acl.GetExplicitEntriesFromAcl()[0]

    ace_access_mode = ace["AccessMode"]
    ace_permissions = ace["AccessPermissions"]
    ace_inheritance = ace["Inheritance"]
    ace_sid = ace["Trustee"]["Identifier"]

    assert ace_sid == user_sid
    assert (
        ace_permissions == windows_permissions.ACCESS_PERMISSIONS_FULL_CONTROL
        and ace_access_mode == windows_permissions.ACCESS_MODE_GRANT_ACCESS
    )
    assert ace_inheritance == windows_permissions.INHERITANCE_OBJECT_AND_CONTAINER


def _get_acl_and_sid_from_path(path: WindowsPath):
    sid, _, _ = win32security.LookupAccountName("", win32api.GetUserName())
    security_descriptor = win32security.GetNamedSecurityInfo(
        str(path), win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION
    )
    acl = security_descriptor.GetSecurityDescriptorDacl()
    return acl, sid


def assert_linux_permissions(path: PosixPath):
    st = os.stat(path)

    expected_mode = stat.S_IRWXU
    actual_mode = st.st_mode & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    assert expected_mode == actual_mode


def add_subdirs_to_dir(parent_dir: Path, subdirs: Iterable[str]) -> Iterable[Path]:
    subdir_paths = [parent_dir / s for s in subdirs]

    for subdir in subdir_paths:
        subdir.mkdir()

    return subdir_paths


def add_files_to_dir(parent_dir: Path, file_names: Iterable[str]) -> Iterable[Path]:
    files = [parent_dir / f for f in file_names]

    for f in files:
        f.touch()

    return files
