import logging
import stat
import warnings
from collections.abc import Callable
from pathlib import Path

from monkeytypes import OperatingSystem

from . import get_os

try:
    if get_os() == OperatingSystem.WINDOWS:
        import win32file
        import win32security

        from .windows_permissions import get_security_descriptor_for_owner_only_permissions
except RuntimeError:
    # The most likely cause of this error is that this module has been imported
    # on MacOS (Darwin). While the code in this module may or may not function
    # properly on Darwin, there is code within this package That is platform
    # agnostic. This error, if not caught, will prevent this entire package
    # from being imported, which is not the desired behavior.
    warnings.warn(
        "OS compatibility check failed: This package may not work properly on this OS.",
        ImportWarning,
    )

logger = logging.getLogger(__name__)


class FailedDirectoryCreationError(Exception):
    pass


def create_secure_directory(path: Path):
    if get_os() == OperatingSystem.WINDOWS:
        make_existing_directory_secure_for_os = _make_existing_directory_secure_windows
        create_secure_directory_for_os = _create_secure_directory_windows
    else:
        make_existing_directory_secure_for_os = _make_existing_directory_secure_linux
        create_secure_directory_for_os = _create_secure_directory_linux

    if path.exists():
        _check_path_is_directory(path)
        _make_existing_directory_secure(make_existing_directory_secure_for_os, path)
    else:
        _create_secure_directory(create_secure_directory_for_os, path)


def _check_path_is_directory(path: Path):
    if not path.is_dir():
        raise FailedDirectoryCreationError(
            f'The path "{path}" already exists and is not a directory'
        )

    logger.info(f"A directory already exists at {path}")


def _make_existing_directory_secure(fn_for_os: Callable, path: Path):
    try:
        fn_for_os(path)
    except Exception as err:
        message = (
            "An error occured while changing the existing directory's permissions"
            f"to be secure: {str(err)}"
        )
        logger.exception(message)
        raise FailedDirectoryCreationError(err)


def _create_secure_directory(fn_for_os: Callable, path: Path):
    try:
        fn_for_os(path)
    except Exception as err:
        message = f"Could not create a secure directory at {path}: {str(err)}"
        logger.error(message)
        raise FailedDirectoryCreationError(message)


def _make_existing_directory_secure_windows(path: Path):
    security_descriptor = get_security_descriptor_for_owner_only_permissions()
    win32security.SetFileSecurity(
        str(path), win32security.DACL_SECURITY_INFORMATION, security_descriptor
    )


def _create_secure_directory_windows(path: Path):
    security_attributes = win32security.SECURITY_ATTRIBUTES()
    security_attributes.SECURITY_DESCRIPTOR = get_security_descriptor_for_owner_only_permissions()
    win32file.CreateDirectory(str(path), security_attributes)


def _make_existing_directory_secure_linux(path: Path):
    path.chmod(mode=stat.S_IRWXU)


def _create_secure_directory_linux(path: Path):
    path.mkdir(mode=stat.S_IRWXU)
