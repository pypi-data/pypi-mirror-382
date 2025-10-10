# errzip - Project Summary

## Overview

**errzip** is a Python package that captures exceptions, generates AI-optimized structured JSON summaries, and **ALWAYS** sends them to LLMs for instant analysis. It's designed for small context windows and low-cost AI operations.

## Key Features

1. **Automatic LLM Integration** - Every exception is automatically sent to Ollama (default), OpenAI, or Claude
2. **Structured JSON Output** - Machine-readable format optimized for AI tools
3. **Smart Stack Frame Selection** - Identifies the most relevant frame (skips stdlib/site-packages)
4. **Built-in Heuristics** - Maps common errors to likely causes and suggestions
5. **Multiple Installation Methods** - Global hook, decorator, or manual
6. **Zero-Crash Design** - Never fails the host program
7. **Minimal Dependencies** - Only requires `requests` beyond stdlib

## Project Structure

```
errzip/
├── errzip/
│   └── __init__.py           # Main package (all code in one file)
├── examples/
│   ├── basic_hook.py         # Global exception hook example
│   ├── decorator_usage.py    # Decorator pattern example
│   ├── manual_summary.py     # Manual summarization example
│   └── test_all_providers.py # LLM provider testing guide
├── setup.py                  # Package configuration
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
├── test_errzip.py            # Comprehensive test suite
├── README.md                 # Full documentation
├── QUICKSTART.md            # 3-minute getting started guide
├── INSTALL.md               # Detailed installation instructions
└── .gitignore               # Git ignore rules
```

## Core Components

### 1. Data Structures
- `FrameInfo` - Represents a stack frame (file, line, function, code)
- `ExceptionSummary` - Complete exception summary with all metadata

### 2. Exception Analysis
- `analyze_exception()` - Maps exception types to causes/suggestions
- `extract_dependencies()` - Identifies packages from stack frames
- `choose_top_frame()` - Selects most relevant frame (prefers user code)

### 3. Summarization
- `summarize_exception()` - Creates structured summary from exception
- `emit_summary()` - Outputs one-liner + JSON to STDERR

### 4. AI Integration (ALWAYS Enabled)
- `send_to_ai()` - Sends summary to configured LLM
- `call_ollama()` - Ollama API client
- `call_openai()` - OpenAI API client
- `call_claude()` - Claude/Anthropic API client

### 5. Public API
- `install_excepthook()` - Global exception hook
- `@summarize_exceptions()` - Function decorator
- `summarize_exception()` - Manual summarization

## Supported Error Types

The heuristics engine recognizes and provides specific guidance for:

- ImportError/ModuleNotFoundError
- KeyError
- AttributeError (including None access)
- FileNotFoundError
- PermissionError
- TypeError (argument mismatches)
- ValueError (parsing errors)
- TimeoutError
- SSL/Certificate errors
- MemoryError

## Configuration

All configuration via environment variables:

### Provider Selection
- `WORKING_AI` - ollama (default), openai, claude, none

### Ollama (Default)
- `OLLAMA_BASE_URL` - Default: http://127.0.0.1:11434
- `OLLAMA_MODEL` - Default: llama3.1

### OpenAI
- `OPENAI_BASE_URL` - Default: https://api.openai.com/v1
- `OPENAI_API_KEY` - Required
- `OPENAI_MODEL` - Default: gpt-4o-mini

### Claude
- `CLAUDE_BASE_URL` - Default: https://api.anthropic.com
- `ANTHROPIC_API_KEY` - Required
- `CLAUDE_MODEL` - Default: claude-3-5-sonnet-latest
- `ANTHROPIC_VERSION` - Default: 2023-06-01

### General
- `ERRSUM_AI_TIMEOUT` - Default: 12.0 seconds
- `ERRSUM_AI_MAX_CHARS` - Default: 20000 characters

## Output Format

Every exception generates three outputs to STDERR:

1. **Human one-liner**: `[errzip] {type}: {msg} at {file}:{line} in {func} | cause: {cause}`
2. **JSON block**: Between `===ERRSUM_JSON_BEGIN===` and `===ERRSUM_JSON_END===`
3. **AI analysis**: Between `===ERRSUM_AI_BEGIN===` and `===ERRSUM_AI_END===`

## Testing

The test suite (`test_errzip.py`) validates:

1. ✅ Heuristics engine (all error types)
2. ✅ Exception summarization
3. ✅ JSON serialization
4. ✅ Decorator functionality (reraise=True/False)
5. ✅ AI configuration parsing
6. ✅ Frame selection logic

All tests pass without external dependencies (except `requests` for full AI testing).

## Development Workflow

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt

# Test
python test_errzip.py

# Run examples
export WORKING_AI=ollama  # or openai, claude, none
python examples/basic_hook.py

# Format code (if using dev tools)
black errzip/
flake8 errzip/
mypy errzip/
```

## Design Decisions

### 1. Single File Package
All code in `errzip/__init__.py` for simplicity and easy distribution.

### 2. ALWAYS Send to LLM
Unlike specs1.md (optional), specs3.md requires ALWAYS sending to LLM. Default provider is Ollama (free, local).

### 3. STDERR for All Output
Human-readable and machine-readable output goes to STDERR to avoid mixing with program stdout.

### 4. Never Crash
All exception handling wrapped in try/except. Even if errzip fails, the host program continues.

### 5. Minimal Dependencies
Only `requests` required beyond stdlib. No heavy ML libraries or complex dependencies.

### 6. Python 3.8+ Compatible
Uses modern features (dataclasses, type hints) while maintaining broad compatibility.

## Use Cases

1. **Development** - Real-time AI insights while coding
2. **Production Monitoring** - Parse JSON logs for automated analysis
3. **CI/CD** - Extract structured error data from test failures
4. **Learning** - Understand errors with AI explanations
5. **Cost Optimization** - Compact JSON minimizes LLM token usage

## Performance Characteristics

- **JSON Size**: Typically 2-5KB per exception
- **LLM Latency**: ~1-3 seconds (Ollama local), ~2-5 seconds (OpenAI/Claude)
- **Overhead**: Minimal - only runs on exceptions
- **Memory**: Low - no persistent state

## Future Enhancements

Potential improvements (not implemented):

- Async LLM calls (non-blocking)
- Custom heuristics plugins
- More LLM providers (Gemini, local models)
- Performance profiling data in summary
- Observability platform integrations
- Exception aggregation/deduplication
- Web dashboard for viewing summaries

## License

MIT

## Compliance

This is a **defensive security tool** only:
- ✅ Analyzes exceptions for debugging
- ✅ Helps developers understand errors
- ✅ Provides actionable suggestions
- ❌ Does NOT harvest credentials
- ❌ Does NOT crawl for secrets
- ❌ Does NOT perform offensive operations

---

**Built by developers, for developers who want AI-powered error analysis without complexity.**
