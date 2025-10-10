"""
Example 4: Test all LLM providers
Demonstrates how to test Ollama, OpenAI, and Claude backends.
"""

import os
import errzip

print("Testing AI Provider Integration\n")
print("="*60)

# Test with a simple exception
def trigger_error():
    """Trigger a simple error for testing."""
    data = {"users": [{"id": 1, "name": "Alice"}]}
    return data["admins"][0]["name"]  # KeyError and then IndexError potential

# Save current provider
original_provider = os.environ.get("WORKING_AI", "ollama")

# Test 1: No AI (just JSON output)
print("\n1. Testing with WORKING_AI=none (no LLM calls)")
print("-" * 60)
os.environ["WORKING_AI"] = "none"
errzip.install_excepthook()

try:
    trigger_error()
except:
    pass

# Test 2: Ollama (default, local)
print("\n2. Testing with WORKING_AI=ollama")
print("-" * 60)
print("Make sure Ollama is running: ollama serve")
print("And model is available: ollama pull llama3.1")
os.environ["WORKING_AI"] = "ollama"
# Uncomment to test:
# try:
#     trigger_error()
# except:
#     pass

# Test 3: OpenAI
print("\n3. Testing with WORKING_AI=openai")
print("-" * 60)
print("Set OPENAI_API_KEY environment variable first")
# os.environ["WORKING_AI"] = "openai"
# os.environ["OPENAI_API_KEY"] = "sk-..."  # Set this externally
# Uncomment to test:
# try:
#     trigger_error()
# except:
#     pass

# Test 4: Claude
print("\n4. Testing with WORKING_AI=claude")
print("-" * 60)
print("Set ANTHROPIC_API_KEY environment variable first")
# os.environ["WORKING_AI"] = "claude"
# os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."  # Set this externally
# Uncomment to test:
# try:
#     trigger_error()
# except:
#     pass

# Restore original
os.environ["WORKING_AI"] = original_provider

print("\n" + "="*60)
print("Provider testing guide complete")
print("\nTo test live:")
print("1. For Ollama: Start server and run this script")
print("2. For OpenAI: export OPENAI_API_KEY=... && python test_all_providers.py")
print("3. For Claude: export ANTHROPIC_API_KEY=... && python test_all_providers.py")
