# errzip

**AI-optimized exception summarization for Python**

`errzip` captures Python exceptions, creates compact structured JSON summaries optimized for small AI context windows, and **ALWAYS** sends them to an LLM (Ollama by default, OpenAI, or Claude) for instant analysis.

## Features

- 🎯 **Automatic LLM Analysis**: Every exception is automatically sent to your configured LLM
- 📊 **Structured JSON Output**: Machine-readable format optimized for AI tools
- 🔍 **Smart Frame Selection**: Identifies the most relevant stack frame (skips stdlib)
- 💡 **Built-in Heuristics**: Common error patterns mapped to likely causes
- 🔌 **Multiple LLM Backends**: Supports Ollama (default), OpenAI, and Claude
- 🛡️ **Zero-Crash Design**: Never fails your program, even if analysis fails
- 📦 **Minimal Dependencies**: Only requires `requests` beyond stdlib

## Installation

```bash
pip install errzip
```

Or install from source:

```bash
git clone https://github.com/yourusername/errzip.git
cd errzip
pip install -e .
```

## Quick Start

### Option 1: Global Exception Hook (Catch All Unhandled Exceptions)

```python
import errzip

# Install the hook - all unhandled exceptions will be analyzed
errzip.install_excepthook()

# Any unhandled exception will be caught, summarized, and sent to LLM
def buggy_function():
    return {}['missing_key']

buggy_function()  # Exception analyzed by AI automatically
```

### Option 2: Decorator (Specific Functions)

```python
import errzip

@errzip.summarize_exceptions(reraise=True)
def risky_operation(filename):
    with open(filename) as f:
        return f.read()

# Exception will be summarized and sent to AI before re-raising
risky_operation('/nonexistent/file.txt')
```

### Option 3: Manual (Programmatic Control)

```python
import errzip

try:
    result = 10 / 0
except Exception as e:
    summary = errzip.summarize_exception(e)
    print(f"Error: {summary.error_type}")
    print(f"Cause: {summary.likely_cause}")
    print(f"Suggestions: {summary.suggestions}")
```

## Configuration

Configure via environment variables:

### Choose Your LLM Provider

```bash
# Ollama (default, free, runs locally)
export WORKING_AI=ollama
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3.1

# OpenAI
export WORKING_AI=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini

# Claude (Anthropic)
export WORKING_AI=claude
export ANTHROPIC_API_KEY=sk-ant-...
export CLAUDE_MODEL=claude-3-5-sonnet-latest

# Disable AI (JSON output only, no LLM calls)
export WORKING_AI=none
```

### General Settings

```bash
export ERRSUM_AI_TIMEOUT=12.0      # Timeout for LLM calls (seconds)
export ERRSUM_AI_MAX_CHARS=20000   # Max JSON size before truncation
```

## Output Format

Every exception generates two outputs to STDERR:

### 1. Human-Readable One-Liner

```
[errzip] builtins.KeyError: 'missing_key' at script.py:15 in buggy_function | cause: Dictionary key does not exist
```

### 2. Machine-Readable JSON

```
===ERRSUM_JSON_BEGIN===
{
  "error_type": "builtins.KeyError",
  "message": "'missing_key'",
  "top_frame": {
    "file": "script.py",
    "line": 15,
    "function": "buggy_function",
    "code": "return x['missing_key']"
  },
  "stack": [...],
  "likely_cause": "Dictionary key does not exist",
  "suggestions": [
    "Verify key exists before access",
    "Use .get() with default",
    "Check data structure"
  ],
  "env": {
    "python_version": "3.11.5",
    "platform": "macOS-14.0-arm64",
    "cwd": "/Users/you/project"
  },
  "dependencies": {...},
  "raw_traceback": "..."
}
===ERRSUM_JSON_END===
```

### 3. AI Analysis (ALWAYS Generated)

```
===ERRSUM_AI_BEGIN===
Error: KeyError accessing missing dictionary key
Location: script.py:15 in buggy_function
Likely cause: Attempting to access a key that doesn't exist in the dictionary
Quick checks:
  - Verify the key 'missing_key' should exist
  - Check if dictionary was populated correctly
  - Add defensive key checking
Fast fix: Use x.get('missing_key', default_value)
===ERRSUM_AI_END===
```

## Why errzip?

### Traditional Error Messages
```
Traceback (most recent call last):
  File "script.py", line 42, in <module>
    process_data()
  File "script.py", line 38, in process_data
    return data['result']['value']
KeyError: 'result'
```

### With errzip
```
[errzip] builtins.KeyError: 'result' at script.py:38 in process_data | cause: Dictionary key does not exist

===ERRSUM_AI_BEGIN===
Error: Missing 'result' key in dictionary
Location: script.py:38 in process_data
Likely cause: API response doesn't contain expected 'result' key
Quick checks:
  - Verify API endpoint is returning correct structure
  - Check if request completed successfully
  - Add response validation
Fast fix: Use data.get('result', {}).get('value') or validate response first
===ERRSUM_AI_END===
```

## Built-in Heuristics

`errzip` recognizes common error patterns:

- **ImportError/ModuleNotFoundError** → Missing dependency
- **KeyError** → Dictionary key doesn't exist
- **AttributeError** → Missing attribute or None access
- **FileNotFoundError** → Wrong path or working directory
- **PermissionError** → Insufficient OS permissions
- **TypeError** (positional arguments) → Function arity mismatch
- **ValueError** (invalid literal) → Parsing failure
- **TimeoutError** → Operation exceeded time limit
- **SSL errors** → Certificate validation issues
- **MemoryError** → Out of memory

## API Reference

### `install_excepthook()`
Installs global exception hook to catch all unhandled exceptions.

### `@summarize_exceptions(reraise=True)`
Decorator to summarize exceptions in specific functions.
- `reraise=True`: Re-raises exception after summarizing
- `reraise=False`: Swallows exception, returns None

### `summarize_exception(exc: BaseException) -> ExceptionSummary`
Manually create a summary of an exception. Returns `ExceptionSummary` dataclass.

## Use Cases

- **Development**: Get instant AI insights on errors as you code
- **Production Monitoring**: Parse JSON logs for automated error analysis
- **CI/CD**: Extract structured error data from test failures
- **Learning**: Understand why exceptions happen with AI explanations
- **Cost Optimization**: Minimize LLM token usage with compact JSON format

## How It Works

1. **Exception Captured**: Via hook, decorator, or manual call
2. **Stack Analysis**: Extracts frames, identifies user code vs stdlib
3. **Heuristics Applied**: Maps error type/message to likely causes
4. **JSON Generation**: Creates compact, structured summary (~2-5KB typical)
5. **LLM Call**: ALWAYS sends to configured LLM (unless `WORKING_AI=none`)
6. **Output**: Emits human line, JSON, and AI analysis to STDERR

## Safety & Security

- ✅ Never crashes your program (all operations wrapped)
- ✅ No secrets logged (only necessary env vars used)
- ✅ Network failures handled gracefully
- ✅ Works offline (if `WORKING_AI=none`)

## Requirements

- Python 3.8+
- `requests` library

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.

## Roadmap

- [ ] Async LLM calls (non-blocking)
- [ ] Custom heuristics plugins
- [ ] More LLM providers (Gemini, etc.)
- [ ] Performance profiling data in summary
- [ ] Integration with observability platforms

---

**Built for developers who want AI-powered error analysis without the overhead.**
