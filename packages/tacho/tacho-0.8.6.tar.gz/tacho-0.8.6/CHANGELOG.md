# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.6] - 2025-02-08

### Fixed
- Added automatic retry logic (up to 3 attempts) for transient API errors during model validation and benchmarking
- Fixed `openai/gpt-5-codex` and similar models that occasionally fail with `InternalServerError` or `APIConnectionError` on first request
- Improved error handling to distinguish between retryable errors (connection issues, internal server errors) and permanent failures (authentication, not found, rate limits)

## [0.8.5] - 2025-02-03

### Fixed
- Fixed tests to match refactored CLI structure (updated from removed `bench`/`ping` functions to unified `cli` function)
- Fixed `test_invalid_model_handling` to mock API calls and prevent failures in CI environments
- Increased validation ping tokens from 10 to 20 to support newer OpenAI models with minimum token requirements
- Increased generic error message truncation from 100 to 200 characters for better debugging

## [0.8.1] - 2025-01-31

### Added
- Parameter validation: `--runs` and `--tokens` now require positive values (minimum of 1)

### Fixed
- Fixed issue where zero or negative values for `--runs` and `--tokens` were accepted but caused unclear behavior

## [0.8.0] - 2025-01-31

### Changed
- **BREAKING**: Simplified CLI to single-purpose tool - removed `bench` and `ping` subcommands
- The tool now benchmarks models directly: `tacho model1 model2`
- Fixed help system - `--help` now works correctly in all contexts
- Options can now be placed anywhere in the command: `tacho model -r 3` or `tacho -r 3 model`

### Removed
- Removed `ping` subcommand (validation still happens automatically before benchmarking)
- Removed subcommand structure entirely for cleaner, more intuitive usage

## [0.7.1] - 2025-01-30

### Added
- Comprehensive error handling tests for all major LiteLLM error types
- User-friendly error messages for different error scenarios:
  - Authentication errors now show which API key to check
  - Model not found errors suggest checking the model name
  - Rate limit errors advise trying again later
  - Connection errors for Ollama specifically mention starting the server
  - Generic errors are truncated to 80 characters for readability

### Changed
- Simplified error handling by focusing on the most common error types
- Improved error message formatting with consistent capitalization

## [0.7.0] - 2025-01-30

### Added
- "Avg Tokens" column in benchmark results table showing average tokens generated per model

## [0.6.0] - 2025-01-29

### Added
- Comprehensive unit test suite with 31 tests covering all major components

### Changed
- Renamed `--lim` to `--tokens`


## [0.5.0] - 2025-01-27

### Added
- Automatic configuration file at `~/.tacho/.env` for storing API keys
- Configuration file is created on first run with helpful comments
- API keys from configuration file are loaded automatically on startup
- Cross-platform support for Windows, macOS, and Linux

### Changed
- Moved logging configuration to `config.py` module for better organization
- Environment variables now have two sources: ~/.tacho/.env file and system environment (system takes precedence)

### Security
- Configuration file is created with restrictive permissions (600) on Unix-like systems

## [0.4.0] - 2025-01-27

### Added
- New `ping` command to check model availability without running benchmarks
- Tests for the ping command functionality

### Fixed
- CLI callback logic to properly handle subcommands

## [0.3.0] - 2025-01-26

### Changed
- Improved error handling with specific exception types for authentication, rate limits, and connection issues
- Enhanced user feedback with clearer error messages during model validation
- Added graceful handling of keyboard interrupts (Ctrl+C)
- Updated README to accurately reflect output metrics

### Fixed
- Corrected README documentation about displayed metrics (removed mention of median and average tokens)

## [0.2.1] - 2025-01-26

### Changed
- Major code refactoring for improved elegance and maintainability
- Unified benchmark functions to eliminate code duplication (~80 lines removed)
- Simplified progress tracking by removing complex queue system
- Cleaner CLI argument handling using Typer's callback feature
- Extracted metrics calculation into reusable helper function
- Improved error handling with cleaner validation messages
- Reduced total codebase by ~15% while maintaining all functionality

### Fixed
- Fixed module import issues in pyproject.toml entry point

## [0.1.5] - 2025-01-26

### Changed
- Display average time and tokens per run instead of totals
- Improved clarity of benchmark metrics

## [0.1.4] - 2025-01-26

### Added
- `--lim` parameter to control maximum tokens per response (default: 2000)
- Full async/parallel execution for all benchmarks

### Changed
- Tokens/second is now the primary metric instead of raw time
- All benchmarks run in parallel by default
- Simplified progress indicators to just spinners

### Removed
- Sequential benchmark mode (everything is now parallel)
- Hardcoded provider list in favor of dynamic testing
- Individual model completion outputs during benchmarking
- "Fastest model" announcement at the end

## [0.1.3] - 2025-01-26

### Changed
- Reorganized package structure: moved CLI code to separate module
- Updated entry point configuration

## [0.1.2] - 2025-01-26

### Changed
- Fixed import issues with package entry point

## [0.1.1] - 2025-01-26

### Added
- Initial release
- Basic benchmarking functionality
- Support for multiple LLM providers via LiteLLM
- Progress bars and formatted output tables
- `list-providers` command