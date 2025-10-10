"""
errzip - AI-optimized exception summarization package
Captures exceptions, creates structured JSON summaries, and ALWAYS sends them to LLMs for analysis.
"""

import sys
import os
import json
import traceback
import linecache
import platform
import functools
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Callable
import importlib.metadata


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class FrameInfo:
    """Represents a single stack frame."""
    file: str
    line: int
    function: str
    code: Optional[str]


@dataclass
class ExceptionSummary:
    """Structured exception summary optimized for AI consumption."""
    error_type: str
    message: str
    top_frame: FrameInfo
    stack: List[FrameInfo]
    likely_cause: Optional[str]
    suggestions: List[str]
    env: Dict[str, str]
    dependencies: Dict[str, str]
    raw_traceback: str


# ============================================================================
# HEURISTICS - Map exceptions to causes and suggestions
# ============================================================================

def analyze_exception(exc_type: type, exc_value: BaseException, tb) -> tuple[Optional[str], List[str]]:
    """
    Analyze exception and return (likely_cause, suggestions).
    Uses simple heuristics based on exception type and message.
    """
    exc_name = exc_type.__name__
    exc_msg = str(exc_value).lower()

    # Import errors
    if exc_name in ('ImportError', 'ModuleNotFoundError'):
        return (
            "Missing or incorrectly named dependency",
            ["Check package is installed", "Verify import spelling", "Check Python path"]
        )

    # Key errors
    if exc_name == 'KeyError':
        return (
            "Dictionary key does not exist",
            ["Verify key exists before access", "Use .get() with default", "Check data structure"]
        )

    # Attribute errors
    if exc_name == 'AttributeError':
        if 'nonetype' in exc_msg or 'none' in exc_msg:
            return (
                "Attempted to access attribute on None",
                ["Check for None before access", "Add null checks", "Verify initialization"]
            )
        return (
            "Object missing expected attribute",
            ["Check object type", "Verify attribute name", "Check API version"]
        )

    # File errors
    if exc_name == 'FileNotFoundError':
        return (
            "File path incorrect or working directory mismatch",
            ["Verify file path", "Check current working directory", "Use absolute paths"]
        )

    # Permission errors
    if exc_name == 'PermissionError':
        return (
            "Insufficient OS permissions",
            ["Check file/directory permissions", "Run with appropriate privileges", "Verify ownership"]
        )

    # Type errors
    if exc_name == 'TypeError':
        if 'positional' in exc_msg or 'argument' in exc_msg:
            return (
                "Function called with wrong number of arguments",
                ["Check function signature", "Verify argument count", "Review API documentation"]
            )
        return (
            "Type mismatch in operation",
            ["Check variable types", "Add type validation", "Review type hints"]
        )

    # Value errors
    if exc_name == 'ValueError':
        if 'invalid literal' in exc_msg:
            return (
                "Failed to parse value",
                ["Validate input format", "Add error handling", "Check data source"]
            )
        return (
            "Invalid value for operation",
            ["Check input range", "Validate parameters", "Review constraints"]
        )

    # Timeout errors
    if exc_name in ('TimeoutError', 'asyncio.TimeoutError'):
        return (
            "Operation exceeded time limit",
            ["Increase timeout value", "Check network connectivity", "Optimize operation"]
        )

    # SSL/Certificate errors
    if 'ssl' in exc_name.lower() or 'certificate' in exc_msg:
        return (
            "SSL/TLS certificate validation failed",
            ["Check certificate validity", "Verify hostname", "Update CA certificates"]
        )

    # Memory errors
    if exc_name == 'MemoryError':
        return (
            "Insufficient memory available",
            ["Reduce data size", "Process in batches", "Increase system memory"]
        )

    # Default
    return (None, ["Check error message and stack trace", "Review recent code changes"])


# ============================================================================
# STACK FRAME ANALYSIS
# ============================================================================

def is_stdlib_or_sitepackages(filepath: str) -> bool:
    """Check if filepath is from stdlib or site-packages."""
    normalized = filepath.replace('\\', '/')
    return (
        '/site-packages/' in normalized or
        '/dist-packages/' in normalized or
        normalized.startswith('<') or  # <frozen>, <string>, etc.
        'python3.' in normalized.split('/')[-3:-1].__str__() or
        '/lib/python' in normalized
    )


def choose_top_frame(frames: List[FrameInfo]) -> FrameInfo:
    """
    Choose the most relevant frame for error reporting.
    Prefers last user code frame, falls back to last frame overall.
    """
    if not frames:
        return FrameInfo(file="<unknown>", line=0, function="<unknown>", code=None)

    # Try to find last frame not in stdlib/site-packages
    for frame in reversed(frames):
        if not is_stdlib_or_sitepackages(frame.file):
            return frame

    # Fall back to last frame
    return frames[-1]


def extract_dependencies(frames: List[FrameInfo]) -> Dict[str, str]:
    """
    Extract package names and versions from stack frames.
    Limits to top 10 packages.
    """
    packages = set()

    for frame in frames:
        # Look for site-packages in path
        if '/site-packages/' in frame.file:
            parts = frame.file.split('/site-packages/')
            if len(parts) > 1:
                # Get package name (first component after site-packages)
                pkg_path = parts[1].split('/')[0]
                # Strip version info if present
                pkg_name = pkg_path.split('-')[0]
                if pkg_name and not pkg_name.startswith('_'):
                    packages.add(pkg_name)

    # Get versions
    result = {}
    for pkg in sorted(packages)[:10]:  # Limit to 10
        try:
            version = importlib.metadata.version(pkg)
            result[pkg] = version
        except Exception:
            result[pkg] = "unknown"

    return result


# ============================================================================
# EXCEPTION SUMMARIZATION
# ============================================================================

def summarize_exception(exc: BaseException) -> ExceptionSummary:
    """
    Create structured summary of an exception.
    Returns ExceptionSummary dataclass with all analysis.
    """
    exc_type = type(exc)
    exc_value = exc
    tb = exc.__traceback__

    # Extract stack frames
    frames = []
    if tb:
        extracted = traceback.extract_tb(tb)
        for frame in extracted:
            code = linecache.getline(frame.filename, frame.lineno).strip() if frame.filename else None
            frames.append(FrameInfo(
                file=frame.filename,
                line=frame.lineno,
                function=frame.name,
                code=code
            ))

    # Choose top frame
    top_frame = choose_top_frame(frames)

    # Analyze exception
    likely_cause, suggestions = analyze_exception(exc_type, exc_value, tb)

    # Extract dependencies
    dependencies = extract_dependencies(frames)

    # Build environment info
    env = {
        "python_version": platform.python_version(),
        "executable": sys.executable,
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "argv": " ".join(sys.argv)
    }

    # Get raw traceback
    raw_tb = "".join(traceback.format_exception(exc_type, exc_value, tb))

    return ExceptionSummary(
        error_type=f"{exc_type.__module__}.{exc_type.__name__}",
        message=str(exc_value),
        top_frame=top_frame,
        stack=frames,
        likely_cause=likely_cause,
        suggestions=suggestions,
        env=env,
        dependencies=dependencies,
        raw_traceback=raw_tb
    )


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def emit_summary(summary: ExceptionSummary) -> None:
    """
    Emit human-readable one-liner and machine-readable JSON to STDERR.
    Never raises exceptions.
    """
    try:
        # Human-readable one-liner
        tf = summary.top_frame
        cause_str = f" | cause: {summary.likely_cause}" if summary.likely_cause else ""
        one_liner = f"[errzip] {summary.error_type}: {summary.message} at {tf.file}:{tf.line} in {tf.function}{cause_str}\n"
        sys.stderr.write(one_liner)
        sys.stderr.flush()

        # Machine-readable JSON
        sys.stderr.write("===ERRSUM_JSON_BEGIN===\n")

        # Convert dataclass to dict, handling nested dataclasses
        def convert_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return asdict(obj)
            return obj

        summary_dict = asdict(summary)
        json_str = json.dumps(summary_dict, indent=2)
        sys.stderr.write(json_str + "\n")

        sys.stderr.write("===ERRSUM_JSON_END===\n")
        sys.stderr.flush()

    except Exception as e:
        # Emergency fallback - never crash
        sys.stderr.write(f"[errzip] Internal error during summary emission: {e}\n")
        sys.stderr.flush()


# ============================================================================
# AI INTEGRATION - ALWAYS enabled
# ============================================================================

def get_env_bool(key: str, default: bool = False) -> bool:
    """Parse environment variable as boolean."""
    val = os.environ.get(key, "").lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


def get_ai_config() -> Dict[str, Any]:
    """
    Read AI configuration from environment.
    Returns dict with provider and settings.
    """
    # Provider selection - default to ollama for ALWAYS-send behavior
    provider = os.environ.get("WORKING_AI", "ollama").lower()

    return {
        "provider": provider,
        "autosend": True,  # ALWAYS send to LLM
        "timeout": float(os.environ.get("ERRSUM_AI_TIMEOUT", "12.0")),
        "max_chars": int(os.environ.get("ERRSUM_AI_MAX_CHARS", "20000")),
        # Ollama
        "ollama_base_url": os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        "ollama_model": os.environ.get("OLLAMA_MODEL", "llama3.1"),
        # OpenAI
        "openai_base_url": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
        "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        # Claude
        "claude_base_url": os.environ.get("CLAUDE_BASE_URL", "https://api.anthropic.com"),
        "claude_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "claude_model": os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-latest"),
        "anthropic_version": os.environ.get("ANTHROPIC_VERSION", "2023-06-01"),
    }


def call_ollama(config: Dict[str, Any], user_prompt: str) -> str:
    """Call Ollama API."""
    try:
        import requests
    except ImportError:
        return "ERROR: requests library not installed"

    url = f"{config['ollama_base_url']}/api/chat"

    payload = {
        "model": config["ollama_model"],
        "messages": [
            {
                "role": "system",
                "content": "You are an expert software diagnostician. Analyze the provided structured exception summary and output a short, actionable diagnosis."
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False
    }

    try:
        resp = requests.post(url, json=payload, timeout=config["timeout"])
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "No response from Ollama")
    except Exception as e:
        return f"Ollama error: {e}"


def call_openai(config: Dict[str, Any], user_prompt: str) -> str:
    """Call OpenAI API."""
    try:
        import requests
    except ImportError:
        return "ERROR: requests library not installed"

    if not config["openai_api_key"]:
        return "ERROR: OPENAI_API_KEY not set"

    url = f"{config['openai_base_url']}/chat/completions"

    headers = {
        "Authorization": f"Bearer {config['openai_api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config["openai_model"],
        "messages": [
            {
                "role": "system",
                "content": "You are an expert software diagnostician. Analyze the provided structured exception summary and output a short, actionable diagnosis."
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=config["timeout"])
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from OpenAI")
    except Exception as e:
        return f"OpenAI error: {e}"


def call_claude(config: Dict[str, Any], user_prompt: str) -> str:
    """Call Claude (Anthropic) API."""
    try:
        import requests
    except ImportError:
        return "ERROR: requests library not installed"

    if not config["claude_api_key"]:
        return "ERROR: ANTHROPIC_API_KEY not set"

    url = f"{config['claude_base_url']}/v1/messages"

    headers = {
        "x-api-key": config["claude_api_key"],
        "anthropic-version": config["anthropic_version"],
        "Content-Type": "application/json"
    }

    payload = {
        "model": config["claude_model"],
        "max_tokens": 1024,
        "system": "You are an expert software diagnostician. Analyze the provided structured exception summary and output a short, actionable diagnosis.",
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=config["timeout"])
        resp.raise_for_status()
        data = resp.json()
        # Extract text from first content block
        content_blocks = data.get("content", [])
        if content_blocks:
            return content_blocks[0].get("text", "No text in Claude response")
        return "No content in Claude response"
    except Exception as e:
        return f"Claude error: {e}"


def send_to_ai(summary: ExceptionSummary) -> None:
    """
    Send exception summary to LLM for analysis.
    ALWAYS attempts to send (unless provider is 'none').
    Outputs AI analysis to STDERR between markers.
    Never raises exceptions.
    """
    try:
        config = get_ai_config()

        # Skip if provider is none
        if config["provider"] == "none":
            return

        # Build user prompt with JSON summary (truncated)
        summary_dict = asdict(summary)
        json_str = json.dumps(summary_dict, indent=2)

        # Truncate if needed
        if len(json_str) > config["max_chars"]:
            json_str = json_str[:config["max_chars"]] + "\n... [truncated]"

        user_prompt = f"""Analyze this exception and provide:
- Error: Brief description
- Location: Where it occurred
- Likely cause: Root cause analysis
- Quick checks: Bulleted list of things to verify
- Fast fix: One-line suggested fix
- If library-specific: Any library-specific notes

Exception Summary:
{json_str}
"""

        # Call appropriate provider
        if config["provider"] == "ollama":
            ai_response = call_ollama(config, user_prompt)
        elif config["provider"] == "openai":
            ai_response = call_openai(config, user_prompt)
        elif config["provider"] == "claude":
            ai_response = call_claude(config, user_prompt)
        else:
            ai_response = f"Unknown provider: {config['provider']}"

        # Emit AI response
        sys.stderr.write("===ERRSUM_AI_BEGIN===\n")
        sys.stderr.write(ai_response + "\n")
        sys.stderr.write("===ERRSUM_AI_END===\n")
        sys.stderr.flush()

    except Exception as e:
        # Emergency fallback
        try:
            sys.stderr.write("===ERRSUM_AI_BEGIN===\n")
            sys.stderr.write(f"AI analysis failed: {e}\n")
            sys.stderr.write("===ERRSUM_AI_END===\n")
            sys.stderr.flush()
        except:
            pass  # Absolute last resort - silently fail


# ============================================================================
# PUBLIC API
# ============================================================================

def install_excepthook() -> None:
    """
    Install global exception hook to summarize unhandled exceptions.
    Automatically sends to AI if configured.
    """
    def excepthook(exc_type, exc_value, exc_tb):
        try:
            # Recreate exception with traceback
            exc_value.__traceback__ = exc_tb
            summary = summarize_exception(exc_value)
            emit_summary(summary)
            send_to_ai(summary)
        except Exception as e:
            sys.stderr.write(f"[errzip] Critical error in excepthook: {e}\n")
            sys.stderr.flush()

        # Call original excepthook
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = excepthook


def summarize_exceptions(reraise: bool = True) -> Callable:
    """
    Decorator to summarize exceptions in wrapped function.

    Args:
        reraise: If True, re-raise the exception after summarizing

    Usage:
        @summarize_exceptions()
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                try:
                    summary = summarize_exception(e)
                    emit_summary(summary)
                    send_to_ai(summary)
                except Exception as summary_error:
                    sys.stderr.write(f"[errzip] Error during summarization: {summary_error}\n")
                    sys.stderr.flush()

                if reraise:
                    raise
                return None

        return wrapper
    return decorator


# ============================================================================
# USAGE EXAMPLES (as docstring)
# ============================================================================

"""
EXAMPLE 1: Install global exception hook
-----------------------------------------
import errzip

# Install the hook to catch unhandled exceptions
errzip.install_excepthook()

# Any unhandled exception will be summarized and sent to AI
def buggy_function():
    x = {}
    return x['missing_key']

buggy_function()  # Will be caught, summarized, and sent to LLM


EXAMPLE 2: Decorator for specific functions
--------------------------------------------
import errzip

@errzip.summarize_exceptions(reraise=True)
def risky_operation(filename):
    with open(filename) as f:
        return f.read()

# Exception will be summarized and sent to AI before re-raising
risky_operation('/nonexistent/file.txt')


EXAMPLE 3: Manual summarization
--------------------------------
import errzip

try:
    result = 10 / 0
except Exception as e:
    summary = errzip.summarize_exception(e)
    # summary is an ExceptionSummary dataclass
    print(f"Error type: {summary.error_type}")
    print(f"Message: {summary.message}")
    print(f"Suggestions: {summary.suggestions}")


CONFIGURATION
-------------
Environment variables:

# Provider (ollama, openai, claude, none)
export WORKING_AI=ollama  # default

# Ollama settings (default provider)
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3.1

# OpenAI settings
export WORKING_AI=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini

# Claude settings
export WORKING_AI=claude
export ANTHROPIC_API_KEY=sk-ant-...
export CLAUDE_MODEL=claude-3-5-sonnet-latest

# General settings
export ERRSUM_AI_TIMEOUT=12.0
export ERRSUM_AI_MAX_CHARS=20000


ACCEPTANCE TESTS
----------------
Test 1: Basic exception capture
- Run: python -c "import errzip; errzip.install_excepthook(); x = {}; x['key']"
- Expected: One-liner to stderr, JSON between markers, parseable JSON

Test 2: AI integration with Ollama
- Set: export WORKING_AI=ollama
- Run: Same as Test 1
- Expected: AI analysis between ===ERRSUM_AI_BEGIN/END=== markers

Test 3: AI integration with OpenAI
- Set: export WORKING_AI=openai, export OPENAI_API_KEY=...
- Run: Same as Test 1
- Expected: OpenAI analysis in AI markers

Test 4: Decorator usage
- Test reraise=True and reraise=False
- Verify summary emitted in both cases
- Verify exception propagates only when reraise=True

Test 5: Heuristics validation
- Test ImportError → suggests checking package installation
- Test KeyError → suggests using .get() method
- Test FileNotFoundError → suggests checking path
"""
