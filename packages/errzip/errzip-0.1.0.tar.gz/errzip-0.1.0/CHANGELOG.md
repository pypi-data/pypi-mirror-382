# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-09

### Added
- Initial release of errzip
- Exception capture via global hook, decorator, or manual call
- Automatic LLM integration (Ollama, OpenAI, Claude)
- Structured JSON output optimized for AI consumption
- Smart stack frame selection (prefers user code over stdlib)
- Built-in heuristics for 10+ common exception types:
  - ImportError/ModuleNotFoundError
  - KeyError
  - AttributeError
  - FileNotFoundError
  - PermissionError
  - TypeError
  - ValueError
  - TimeoutError
  - SSL/Certificate errors
  - MemoryError
- Environment info collection (Python version, platform, cwd, argv)
- Dependency extraction from stack traces
- Comprehensive test suite
- Example scripts for all usage patterns
- Full documentation (README, QUICKSTART, INSTALL guides)

### Features
- `install_excepthook()` - Install global exception handler
- `@summarize_exceptions(reraise=True)` - Decorator for specific functions
- `summarize_exception(exc)` - Manual exception summarization
- Output format:
  - Human-readable one-liner to STDERR
  - Structured JSON between markers
  - AI analysis between markers (ALWAYS generated)
- Configuration via environment variables
- Support for Ollama (default), OpenAI, and Claude
- Zero-crash design - never fails host program
- Python 3.8+ compatibility
- Minimal dependencies (only requests)

### Documentation
- README.md - Complete documentation
- QUICKSTART.md - 3-minute getting started guide
- INSTALL.md - Detailed installation instructions
- PROJECT_SUMMARY.md - Technical overview
- Examples for all usage patterns

[0.1.0]: https://github.com/yourusername/errzip/releases/tag/v0.1.0
