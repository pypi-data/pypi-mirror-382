# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-06

### Added
- Modern Python packaging with `pyproject.toml`
- Comprehensive MANIFEST.in for package distribution
- Optional pandas dependency support via extras
- Improved error handling with detailed error messages
- Better compatibility with backend API responses

### Changed
- Upgraded from setup.py-only to modern pyproject.toml configuration
- Made pandas an optional dependency (install with `pip install qdf-sdk[pandas]`)
- Improved response unwrapping for nested API responses
- Enhanced retry logic with exponential backoff

### Fixed
- Fixed pool detail endpoint response parsing
- Removed invalid `volume_24h` metric (column doesn't exist in database)
- Corrected parameter mappings for sorting options
- Fixed compatibility issues with backend validation models
- Improved handling of missing optional fields in API responses

### Performance
- SDK test success rate improved from 52% to 95%
- Better handling of rate limits with automatic retries
- Optimized dependency management

## [0.1.3] - 2025-01-05

### Fixed
- Fixed SDK MacroLiveData model to match backend response format
- Improved compatibility with backend API

## [0.1.2] - 2025-01-05

### Added
- Parameter mappings for improved usability
- Better documentation in README

## [0.1.1] - 2025-01-04

### Fixed
- Critical SDK issues with API compatibility
- Response parsing errors

## [0.1.0] - 2025-01-03

### Added
- Initial release of QDF SDK
- Support for pool rankings and analytics
- Integration with QuantDeFi API
- Basic client functionality with retry logic
- Pydantic v2 models for type safety
- Support for 60+ blockchains and 7,000+ pools