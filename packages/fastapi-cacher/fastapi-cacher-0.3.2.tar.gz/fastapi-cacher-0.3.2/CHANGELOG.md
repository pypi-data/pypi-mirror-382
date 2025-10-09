# Changelog

## [0.3.0] - 2024-07-10:

### Added

- Support for sliding window expiration mechanism.

## [0.2.0] - 2024-07-08:

### Added

- Support for MongoDB cache: `MongoCache`.
- Support for Authorization header in `cache.cached` decorator.
- Support for JSON body in `cache.cached` decorator.
- Support for dynamic `Request` and `Response` parameters names in the function signature.

### Fixed

- Issue with json parsing of MemCache results.

### Changed

- `default_timeout` in RedisCache from 150 to 300.
- Updated README file with more examples.

## [0.1.0] - 2024-06-24 initial release

### Added

- Initial release of the package.
