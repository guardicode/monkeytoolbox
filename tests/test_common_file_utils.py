import os
from io import BytesIO

import pytest
from tests.utils import add_files_to_dir, add_subdirs_to_dir

from monkeytoolbox import (
    InvalidPath,
    expand_path,
    get_all_regular_files_in_directory,
    get_binary_io_sha256_hash,
)


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

    expected_return_value = []
    assert list(get_all_regular_files_in_directory(tmp_path)) == expected_return_value


def test_get_all_regular_files_in_directory__has_files(tmp_path, monkeypatch):
    add_subdirs_to_dir(tmp_path, SUBDIRS)
    files = add_files_to_dir(tmp_path, FILES)

    expected_return_value = sorted(files)
    assert sorted(get_all_regular_files_in_directory(tmp_path)) == expected_return_value


def test_get_all_regular_files_in_directory__subdir_has_files(tmp_path, monkeypatch):
    subdirs = add_subdirs_to_dir(tmp_path, SUBDIRS)
    add_files_to_dir(subdirs[0], FILES)

    files = add_files_to_dir(tmp_path, FILES)

    expected_return_value = sorted(files)
    assert sorted(get_all_regular_files_in_directory(tmp_path)) == expected_return_value
