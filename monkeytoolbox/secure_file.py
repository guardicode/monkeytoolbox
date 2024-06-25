import logging
import os
import stat
import warnings
from collections.abc import Generator
from contextlib import contextmanager

from monkeytypes import OperatingSystem

from . import get_os

try:
    if get_os() == OperatingSystem.WINDOWS:
        import win32file
        import win32job
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


@contextmanager
def open_new_securely_permissioned_file(path: str, mode: str = "w") -> Generator:
    if get_os() == OperatingSystem.WINDOWS:
        # TODO: Switch from string to Path object to avoid this hack.
        fd = _get_file_descriptor_for_new_secure_file_windows(str(path))
    else:
        fd = _get_file_descriptor_for_new_secure_file_linux(path)

    with open(fd, mode) as f:
        yield f


def _get_file_descriptor_for_new_secure_file_linux(path: str) -> int:
    try:
        mode = stat.S_IRUSR | stat.S_IWUSR
        flags = (
            os.O_RDWR | os.O_CREAT | os.O_EXCL
        )  # read/write, create new, throw error if file exists
        fd = os.open(path, flags, mode)

        return fd

    except Exception as ex:
        logger.error(f'Could not create a file at "{path}": {str(ex)}')
        raise ex


def _get_file_descriptor_for_new_secure_file_windows(path: str) -> int:
    try:
        file_access = win32file.GENERIC_READ | win32file.GENERIC_WRITE

        # Enables other processes to open this file with read-only access.
        # Attempts by other processes to open the file for writing while this
        # process still holds it open will fail.
        file_sharing = win32file.FILE_SHARE_READ

        security_attributes = win32security.SECURITY_ATTRIBUTES()
        security_attributes.SECURITY_DESCRIPTOR = (
            get_security_descriptor_for_owner_only_permissions()
        )
        file_creation = win32file.CREATE_NEW  # fails if file exists
        file_attributes = win32file.FILE_FLAG_BACKUP_SEMANTICS

        handle = win32file.CreateFile(
            path,
            file_access,
            file_sharing,
            security_attributes,
            file_creation,
            file_attributes,
            _get_null_value_for_win32(),
        )

        detached_handle = handle.Detach()

        return win32file._open_osfhandle(detached_handle, os.O_RDWR)

    except Exception as ex:
        logger.error(f'Could not create a file at "{path}": {str(ex)}')
        raise ex


def _get_null_value_for_win32():
    # https://stackoverflow.com/questions/46800142/in-python-with-pywin32-win32job-the-createjobobject-function-how-do-i-pass-nu  # noqa: E501
    return win32job.CreateJobObject(None, "")
