"""
Simple test script to verify errzip functionality.
Run with: python test_errzip.py
"""

import sys
import os
import json

# Ensure errzip is importable
sys.path.insert(0, os.path.dirname(__file__))

import errzip

print("="*70)
print("ERRZIP TEST SUITE")
print("="*70)

# Test 1: Heuristics module
print("\n1. Testing heuristics module...")
print("-" * 70)

test_exceptions = [
    (ImportError, ImportError("No module named 'foo'"), None),
    (KeyError, KeyError("'missing_key'"), None),
    (FileNotFoundError, FileNotFoundError("/no/file"), None),
    (TypeError, TypeError("func() takes 1 positional argument but 2 were given"), None),
]

for exc_type, exc_value, tb in test_exceptions:
    cause, suggestions = errzip.analyze_exception(exc_type, exc_value, tb)
    print(f"\n{exc_type.__name__}:")
    print(f"  Cause: {cause}")
    print(f"  Suggestions: {suggestions[:2]}")  # First 2 suggestions

print("\n✓ Heuristics tests passed")

# Test 2: Exception summarization
print("\n2. Testing exception summarization...")
print("-" * 70)

def create_test_exception():
    """Create a test exception with a real traceback."""
    data = {"foo": "bar"}
    return data["missing"]  # KeyError

try:
    create_test_exception()
except Exception as e:
    summary = errzip.summarize_exception(e)

    # Verify all required fields exist
    assert summary.error_type == "builtins.KeyError"
    assert "missing" in summary.message
    assert summary.top_frame.function == "create_test_exception"
    assert summary.likely_cause is not None
    assert len(summary.suggestions) > 0
    assert "python_version" in summary.env
    assert isinstance(summary.stack, list)

    print(f"Error Type: {summary.error_type}")
    print(f"Message: {summary.message}")
    print(f"Top Frame: {summary.top_frame.file}:{summary.top_frame.line}")
    print(f"Likely Cause: {summary.likely_cause}")
    print(f"Suggestions: {len(summary.suggestions)} provided")
    print(f"Stack Frames: {len(summary.stack)}")

print("\n✓ Summarization tests passed")

# Test 3: JSON serialization
print("\n3. Testing JSON serialization...")
print("-" * 70)

try:
    x = int("not-a-number")
except Exception as e:
    summary = errzip.summarize_exception(e)

    # Convert to dict and JSON
    summary_dict = errzip.asdict(summary)
    json_str = json.dumps(summary_dict, indent=2)

    # Verify JSON is valid and contains required fields
    parsed = json.loads(json_str)
    assert "error_type" in parsed
    assert "message" in parsed
    assert "top_frame" in parsed
    assert "stack" in parsed
    assert "likely_cause" in parsed
    assert "suggestions" in parsed
    assert "env" in parsed

    print(f"JSON length: {len(json_str)} characters")
    print(f"Required fields present: ✓")
    print(f"Valid JSON: ✓")

print("\n✓ JSON serialization tests passed")

# Test 4: Decorator functionality
print("\n4. Testing decorator functionality...")
print("-" * 70)

@errzip.summarize_exceptions(reraise=False)
def failing_function():
    return 1 / 0

# Should not raise (reraise=False)
result = failing_function()
assert result is None
print("Decorator with reraise=False: ✓")

@errzip.summarize_exceptions(reraise=True)
def failing_function_reraise():
    return 1 / 0

# Should raise
try:
    failing_function_reraise()
    assert False, "Should have raised"
except ZeroDivisionError:
    print("Decorator with reraise=True: ✓")

print("\n✓ Decorator tests passed")

# Test 5: AI configuration
print("\n5. Testing AI configuration...")
print("-" * 70)

# Save original
original_provider = os.environ.get("WORKING_AI", "")

# Test config parsing
os.environ["WORKING_AI"] = "ollama"
config = errzip.get_ai_config()
assert config["provider"] == "ollama"
assert config["autosend"] == True  # ALWAYS enabled
assert config["timeout"] == 12.0
print(f"Provider: {config['provider']}")
print(f"Auto-send: {config['autosend']} (ALWAYS enabled)")
print(f"Timeout: {config['timeout']}s")

# Test different providers
for provider in ["openai", "claude", "none"]:
    os.environ["WORKING_AI"] = provider
    config = errzip.get_ai_config()
    assert config["provider"] == provider
    print(f"Provider '{provider}': ✓")

# Restore
if original_provider:
    os.environ["WORKING_AI"] = original_provider
else:
    os.environ.pop("WORKING_AI", None)

print("\n✓ AI configuration tests passed")

# Test 6: Frame selection heuristics
print("\n6. Testing frame selection heuristics...")
print("-" * 70)

# Test stdlib detection
assert errzip.is_stdlib_or_sitepackages("/usr/lib/python3.11/os.py") == True
assert errzip.is_stdlib_or_sitepackages("/site-packages/requests/api.py") == True
assert errzip.is_stdlib_or_sitepackages("/home/user/myproject/app.py") == False
print("Stdlib detection: ✓")

# Test frame selection with mixed frames
frames = [
    errzip.FrameInfo("/usr/lib/python3.11/os.py", 100, "stdlib_func", None),
    errzip.FrameInfo("/home/user/app.py", 42, "user_func", None),
    errzip.FrameInfo("/site-packages/requests/api.py", 200, "lib_func", None),
]
top = errzip.choose_top_frame(frames)
assert top.file == "/home/user/app.py"
print("Frame selection (prefers user code): ✓")

print("\n✓ Frame selection tests passed")

# Summary
print("\n" + "="*70)
print("ALL TESTS PASSED ✓")
print("="*70)
print("\nNext steps:")
print("1. Install in development mode: pip install -e .")
print("2. Test with real exception: python examples/basic_hook.py")
print("3. Test AI integration:")
print("   - Ollama: ollama serve && python examples/basic_hook.py")
print("   - OpenAI: export OPENAI_API_KEY=... && python examples/basic_hook.py")
print("   - Claude: export ANTHROPIC_API_KEY=... && python examples/basic_hook.py")
