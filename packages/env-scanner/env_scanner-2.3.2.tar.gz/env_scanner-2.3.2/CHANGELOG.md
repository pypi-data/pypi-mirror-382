# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for detecting environment variables in other languages (JavaScript, TypeScript, etc.)
- Configuration file support (.env-scanner.json)
- GitHub Actions integration
- VS Code extension

## [2.3.2] - 2025-10-08

### Fixed
- **False positive filtering**: No longer detects common constants like "DEBUG", "DISABLED", "UNKNOWN", "FOUNDER", etc. as environment variables
- **Minimum length requirement**: Environment variables must be at least 3 characters (filters out single letters like "A", "H")
- **Improved regex patterns**: More strict patterns that require proper context

### Added
- Comprehensive FALSE_POSITIVES list with 40+ common non-env-var constants
- Better filtering for log levels, HTTP methods, status values, roles, and generic constants

### Improved
- Cleaner output with fewer false positives
- More accurate detection focusing on actual environment variable usage
- Better distinction between constants and environment variables

## [2.3.1] - 2025-10-08

### Improved
- **Enhanced directory exclusion**: Now properly skips virtual environments, installed packages, and cache directories
- **Smart venv detection**: Automatically detects and skips site-packages, dist-packages, and venv structures
- **File-level filtering**: Skips compiled Python files (.pyc, .pyo, .pyd) and test fixtures
- **Comprehensive exclusions**: Added support for more IDE directories, build directories, and cache types

### Added
- `should_skip_file()` method to filter unwanted files
- Better pattern matching for wildcard and path-based exclusions
- Additional exclude patterns: .ruff_cache, .hypothesis, htmlcov, .nox, IDE directories

### Fixed
- Scanner no longer reports environment variables from installed third-party packages
- Better handling of nested virtual environment structures

## [2.3.0] - 2025-10-08

### Added
- **Framework Support**: Comprehensive support for Django, Flask, FastAPI/Pydantic, and python-dotenv
- **Django patterns**: `env()`, `env.str()`, `env.int()`, `env.bool()`, `config()` (django-environ, decouple)
- **Flask patterns**: `app.config['VAR']`, `current_app.config['VAR']`
- **Pydantic patterns**: `BaseSettings` classes with automatic field detection, `Field(env='VAR')`
- **Config file scanning**: Support for YAML, JSON, TOML, and INI files
- **Advanced AST parsing**: Framework-specific pattern detection using Python's AST

### Improved
- Added 20+ new regex patterns for comprehensive environment variable detection
- Enhanced detection for f-strings and string interpolation
- Better handling of complex expressions

## [0.1.0] - 2025-10-01

### Added
- Initial release of env-scanner
- Core functionality to scan Python projects for environment variables
- Support for multiple detection patterns:
  - `os.environ.get('VAR')`
  - `os.environ['VAR']`
  - `os.getenv('VAR')`
- Dual detection methods (AST parsing and regex)
- Automatic `.env-example` file generation
- Smart variable grouping by prefix
- Intelligent placeholder value generation based on variable names
- Descriptive comments for common variable patterns
- Command-line interface with multiple commands:
  - `env-scanner scan` - Scan and generate
  - `env-scanner list` - List variables only
  - `env-scanner generate` - Alias for scan
- CLI options:
  - Custom output path
  - Directory exclusions
  - Preview before saving
  - Toggle comments, grouping, and headers
- Python API for programmatic usage
- Comprehensive test suite
- Documentation and examples

### Features
- Zero external dependencies (pure Python)
- Support for Python 3.7+
- Cross-platform compatibility (Windows, macOS, Linux)
- Detailed variable location tracking
- Customizable exclusion patterns
- Verbose logging support

[Unreleased]: https://github.com/yourusername/env-scanner/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/env-scanner/releases/tag/v0.1.0


