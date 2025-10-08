# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project tries to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.3.1] - 2025-10-08

### Changed

- Require cattrs >= 25.2.0
- CI: support Python 3.14


## [0.3.0] - 2025-09-02

### Changed

- `ClubSubscription.club_membership_expiry` from `datetime.datetime` to `datetime.date`


## [0.2.0] - 2025-08-01

### Added

- README
- build backend
- `py.typed` marker

### Changed

- Rename module and class
- Improved docstrings
- Tests use installed version of project

### Fixed

- mypy was specified as runtime dependency


## [0.1.0] - 2025-07-31

Initial release


[0.3.0]: https://github.com/elliot-100/british-cycling-utils/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/elliot-100/british-cycling-utils/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/elliot-100/british-cycling-utils/releases/tag/v0.1.0