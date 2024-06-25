# Changelog
All notable changes to this project will be documented in this
file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
the [PEP 440 version scheme](https://peps.python.org/pep-0440/#version-scheme).


## [0.4.0]
### Fixed
- Error that prevents monkeytoolbox from being imported on Darwin. #6
- Import error in `open_new_securely_permissioned_file()` on Windows. #6

## [0.3.0] - 2024-01-16
### Fixed
- The location of the `py.typed` file so that type checking is now properly
  supported

## [0.2.0] - 2024-01-04
### Added
- `get_os_version()`
- `get_hostname()`
- Support for type checking (py.typed marker file)

### Changed
- `get_os()` raises `RuntimeError` if the operating system is not supported
