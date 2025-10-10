# Quick Start Guide

Get started with errzip in 3 minutes.

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install errzip
pip install -e .
```

## Basic Usage

### 1. Catch All Exceptions (Global Hook)

```python
import errzip

# Install the hook
errzip.install_excepthook()

# Any exception will be analyzed
data = {"users": []}
print(data["admins"])  # KeyError - will be caught and sent to LLM
```

### 2. Wrap Specific Functions (Decorator)

```python
import errzip

@errzip.summarize_exceptions(reraise=True)
def process_file(filename):
    with open(filename) as f:
        return f.read()

# Exception analyzed before re-raising
process_file("/nonexistent.txt")
```

### 3. Manual Analysis

```python
import errzip

try:
    result = int("not-a-number")
except Exception as e:
    summary = errzip.summarize_exception(e)
    print(f"Error: {summary.error_type}")
    print(f"Cause: {summary.likely_cause}")
```

## Configuration

### Using Ollama (Free, Local)

```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3.1

# Set environment
export WORKING_AI=ollama

# Run your code
python your_script.py
```

### Using OpenAI

```bash
export WORKING_AI=openai
export OPENAI_API_KEY=sk-your-key-here
python your_script.py
```

### Using Claude

```bash
export WORKING_AI=claude
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python your_script.py
```

### JSON Only (No AI Calls)

```bash
export WORKING_AI=none
python your_script.py
```

## What You Get

When an exception occurs, errzip outputs to STDERR:

### 1. Human One-Liner
```
[errzip] builtins.KeyError: 'admins' at script.py:8 in main | cause: Dictionary key does not exist
```

### 2. Structured JSON
```json
===ERRSUM_JSON_BEGIN===
{
  "error_type": "builtins.KeyError",
  "message": "'admins'",
  "top_frame": {
    "file": "script.py",
    "line": 8,
    "function": "main",
    "code": "print(data['admins'])"
  },
  "likely_cause": "Dictionary key does not exist",
  "suggestions": [
    "Verify key exists before access",
    "Use .get() with default",
    "Check data structure"
  ],
  "env": {...},
  "stack": [...]
}
===ERRSUM_JSON_END===
```

### 3. AI Analysis (ALWAYS Generated)
```
===ERRSUM_AI_BEGIN===
Error: KeyError accessing missing dictionary key 'admins'
Location: script.py:8 in main
Likely cause: Code assumes 'admins' key exists but it's not in the dictionary
Quick checks:
  - Print the dictionary to see available keys
  - Check where the dictionary is populated
  - Verify data source is correct
Fast fix: Use data.get('admins', []) to provide a default value
===ERRSUM_AI_END===
```

## Test It

```bash
# Run test suite
python test_errzip.py

# Try examples
python examples/basic_hook.py
python examples/decorator_usage.py
python examples/manual_summary.py
```

## Next Steps

- Read [README.md](README.md) for full documentation
- See [INSTALL.md](INSTALL.md) for detailed installation options
- Explore [examples/](examples/) for more usage patterns
- Configure your preferred LLM provider

## Key Features

✅ **ALWAYS sends to LLM** - Every exception gets AI analysis
✅ **Structured JSON** - Machine-readable, optimized for AI
✅ **Smart frame selection** - Highlights your code, not stdlib
✅ **Built-in heuristics** - Common errors mapped to causes
✅ **Never crashes** - Robust error handling throughout
✅ **Multiple LLMs** - Ollama, OpenAI, Claude support

---

**Ready to debug smarter? Get started now!**
