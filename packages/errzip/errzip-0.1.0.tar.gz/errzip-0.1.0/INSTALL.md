# Installation Guide

## Quick Start with Virtual Environment

### 1. Create and activate virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install the package

```bash
# Install in development mode (recommended for development)
pip install -e .

# Or install from PyPI (when published)
pip install errzip
```

### 3. Verify installation

```bash
python -c "import errzip; print('errzip installed successfully')"
```

## Running Tests

```bash
# Activate virtualenv first
source venv/bin/activate

# Run test suite
python test_errzip.py
```

Expected output: All tests should pass with green checkmarks.

## Running Examples

### Basic Exception Hook

```bash
# Set provider to 'none' for testing without AI
export WORKING_AI=none
python examples/basic_hook.py
```

### Test with Ollama (Local LLM)

```bash
# 1. Start Ollama server (in another terminal)
ollama serve

# 2. Pull model if needed
ollama pull llama3.1

# 3. Run example
export WORKING_AI=ollama
python examples/basic_hook.py
```

### Test with OpenAI

```bash
export WORKING_AI=openai
export OPENAI_API_KEY=sk-your-key-here
python examples/basic_hook.py
```

### Test with Claude

```bash
export WORKING_AI=claude
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python examples/basic_hook.py
```

## Development Setup

```bash
# Create virtualenv
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e .
pip install -r requirements-dev.txt

# Run tests
python test_errzip.py

# Run examples
python examples/manual_summary.py
python examples/decorator_usage.py
```

## Troubleshooting

### Import error: No module named 'errzip'

Make sure you've installed the package:
```bash
pip install -e .
```

### Import error: No module named 'requests'

The requests library is required:
```bash
pip install requests
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### AI calls fail with "requests library not installed"

Install requests in your active virtualenv:
```bash
pip install requests
```

### Ollama connection errors

Make sure Ollama is running:
```bash
ollama serve
```

Check the connection:
```bash
curl http://127.0.0.1:11434/api/tags
```

### OpenAI/Claude API errors

Verify your API key is set:
```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

## Uninstallation

```bash
pip uninstall errzip
```

## Publishing to PyPI (for maintainers)

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```
