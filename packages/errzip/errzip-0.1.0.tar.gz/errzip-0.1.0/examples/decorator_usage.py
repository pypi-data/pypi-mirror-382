"""
Example 2: Decorator usage
Use the @summarize_exceptions decorator on specific functions.
"""

import errzip

@errzip.summarize_exceptions(reraise=True)
def read_config(filename):
    """Attempt to read a config file."""
    with open(filename) as f:
        return f.read()

@errzip.summarize_exceptions(reraise=False)
def safe_parse(value):
    """Try to parse a value, but don't crash if it fails."""
    return int(value)

print("Example: Decorator usage\n")

# This will trigger analysis and re-raise
print("1. Attempting to read non-existent file...")
try:
    content = read_config("/nonexistent/config.json")
except FileNotFoundError:
    print("Caught FileNotFoundError (after errzip analysis)\n")

# This will trigger analysis but NOT re-raise
print("2. Attempting to parse invalid integer...")
result = safe_parse("not-a-number")
print(f"Result: {result} (None, because reraise=False)\n")
