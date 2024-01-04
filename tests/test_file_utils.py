import os
import stat
from io import SEEK_SET, BytesIO

import pytest
from monkeytypes import OperatingSystem

from monkeytoolbox import (
    InvalidPath,
    append_bytes,
    create_secure_directory,
    expand_path,
    get_all_regular_files_in_directory,
    get_binary_io_sha256_hash,
    get_os,
    make_fileobj_copy,
    open_new_securely_permissioned_file,
)
from monkeytoolbox.secure_directory import FailedDirectoryCreationError
from tests.utils import (
    add_files_to_dir,
    add_subdirs_to_dir,
    assert_linux_permissions,
    assert_windows_permissions,
)


def is_windows_os():
    return get_os() == OperatingSystem.WINDOWS


@pytest.fixture
def test_path_nested(tmp_path):
    path = tmp_path / "test1" / "test2" / "test3"
    return path


@pytest.fixture
def test_path(tmp_path):
    test_path = "test1"
    path = tmp_path / test_path

    return path


def test_create_secure_directory__no_parent_dir(test_path_nested):
    with pytest.raises(Exception):
        create_secure_directory(test_path_nested)


def test_open_new_securely_permissioned_file__already_exists(test_path):
    os.close(os.open(test_path, os.O_CREAT, stat.S_IRWXU))
    assert os.path.isfile(test_path)

    with pytest.raises(Exception):
        with open_new_securely_permissioned_file(test_path):
            pass


def test_open_new_securely_permissioned_file__no_parent_dir(test_path_nested):
    with pytest.raises(Exception):
        with open_new_securely_permissioned_file(test_path_nested):
            pass


def test_open_new_securely_permissioned_file__write(test_path):
    TEST_STR = b"Hello World"
    with open_new_securely_permissioned_file(test_path, "wb") as f:
        f.write(TEST_STR)

    with open(test_path, "rb") as f:
        assert f.read() == TEST_STR


def test_create_secure_directory__path_exists_as_file(test_path):
    with open(test_path, "w"):
        with pytest.raises(FailedDirectoryCreationError):
            create_secure_directory(test_path)


# Linux-only tests


@pytest.mark.skipif(is_windows_os(), reason="Tests Posix (not Windows) permissions.")
def test_create_secure_directory__already_exists_secure_linux(test_path):
    test_path.mkdir(mode=stat.S_IRWXU)
    create_secure_directory(test_path)

    assert_linux_permissions(test_path)


@pytest.mark.skipif(is_windows_os(), reason="Tests Posix (not Windows) permissions.")
def test_create_secure_directory__already_exists_insecure_linux(test_path):
    test_path.mkdir(mode=0o777)
    create_secure_directory(test_path)

    assert_linux_permissions(test_path)


@pytest.mark.skipif(is_windows_os(), reason="Tests Posix (not Windows) permissions.")
def test_create_secure_directory__perm_linux(test_path):
    create_secure_directory(test_path)

    assert_linux_permissions(test_path)


@pytest.mark.skipif(is_windows_os(), reason="Tests Posix (not Windows) permissions.")
def test_open_new_securely_permissioned_file__perm_linux(test_path):
    with open_new_securely_permissioned_file(test_path):
        pass

    st = os.stat(test_path)

    expected_mode = stat.S_IRUSR | stat.S_IWUSR
    actual_mode = st.st_mode & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    assert expected_mode == actual_mode


# Windows-only tests


@pytest.mark.skipif(not is_windows_os(), reason="Tests Windows (not Posix) permissions.")
def test_create_secure_directory__already_exists_secure_windows(test_path):
    # creates a new secure directory
    create_secure_directory(test_path)
    # attempts to create a new secure directory when one already exists
    create_secure_directory(test_path)

    assert_windows_permissions(test_path)


@pytest.mark.skipif(not is_windows_os(), reason="Tests Windows (not Posix) permissions.")
def test_create_secure_directory__already_exists_insecure_windows(test_path):
    test_path.mkdir()
    create_secure_directory(test_path)

    assert_windows_permissions(test_path)


@pytest.mark.skipif(not is_windows_os(), reason="Tests Windows (not Posix) permissions.")
def test_create_secure_directory__perm_windows(test_path):
    create_secure_directory(test_path)

    assert_windows_permissions(test_path)


@pytest.mark.skipif(not is_windows_os(), reason="Tests Windows (not Posix) permissions.")
def test_open_new_securely_permissioned_file__perm_windows(test_path):
    with open_new_securely_permissioned_file(test_path):
        pass

    assert_windows_permissions(test_path)


def test_make_fileobj_copy():
    TEST_STR = b"Hello World"
    with BytesIO(TEST_STR) as src:
        dst = make_fileobj_copy(src)

        # Writing the assertion this way verifies that both src and dest file handles have had
        # their positions reset to 0.
        assert src.read() == TEST_STR
        assert dst.read() == TEST_STR


def test_make_fileobj_copy_seek_src_to_0():
    TEST_STR = b"Hello World"
    with BytesIO(TEST_STR) as src:
        src.seek(int(len(TEST_STR) / 2))
        dst = make_fileobj_copy(src)

        # Writing the assertion this way verifies that both src and dest file handles have had
        # their positions reset to 0.
        assert src.read() == TEST_STR
        assert dst.read() == TEST_STR


def test_append_bytes__pos_0():
    bytes_io = BytesIO(b"1234 5678")

    append_bytes(bytes_io, b"abcd")

    assert bytes_io.read() == b"1234 5678abcd"


def test_append_bytes__pos_5():
    bytes_io = BytesIO(b"1234 5678")
    bytes_io.seek(5, SEEK_SET)

    append_bytes(bytes_io, b"abcd")

    assert bytes_io.read() == b"5678abcd"
    bytes_io.seek(0, SEEK_SET)
    assert bytes_io.read() == b"1234 5678abcd"


def test_expand_user(patched_home_env):
    input_path = os.path.join("~", "test")
    expected_path = patched_home_env / "test"

    assert expand_path(input_path) == expected_path


def test_expand_vars(home_env_variable, patched_home_env):
    input_path = os.path.join(home_env_variable, "test")
    expected_path = patched_home_env / "test"

    assert expand_path(input_path) == expected_path


def test_expand_path__empty_path_provided():
    with pytest.raises(InvalidPath):
        expand_path("")


def test_get_binary_sha256_hash():
    expected_hash = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    assert get_binary_io_sha256_hash(BytesIO(b"Hello World")) == expected_hash


SUBDIRS = ["subdir1", "subdir2"]
FILES = ["file.jpg.zip", "file.xyz", "1.tar", "2.tgz", "2.png", "2.mpg"]


def test_get_all_regular_files_in_directory__no_files(tmp_path, monkeypatch):
    add_subdirs_to_dir(tmp_path, SUBDIRS)

    assert len(list(get_all_regular_files_in_directory(tmp_path))) == 0


def test_get_all_regular_files_in_directory__has_files(tmp_path, monkeypatch):
    add_subdirs_to_dir(tmp_path, SUBDIRS)
    files = add_files_to_dir(tmp_path, FILES)

    expected_return_value = sorted(files)
    assert sorted(get_all_regular_files_in_directory(tmp_path)) == expected_return_value


def test_get_all_regular_files_in_directory__subdir_has_files(tmp_path, monkeypatch):
    subdirs = list(add_subdirs_to_dir(tmp_path, SUBDIRS))
    add_files_to_dir(subdirs[0], FILES)

    files = add_files_to_dir(tmp_path, FILES)

    expected_return_value = sorted(files)
    assert sorted(get_all_regular_files_in_directory(tmp_path)) == expected_return_value
