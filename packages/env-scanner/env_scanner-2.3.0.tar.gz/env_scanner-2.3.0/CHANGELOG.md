# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for detecting environment variables in other languages (JavaScript, TypeScript, etc.)
- Integration with popular .env libraries (python-dotenv, etc.)
- Configuration file support (.env-scanner.json)
- GitHub Actions integration
- VS Code extension

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


