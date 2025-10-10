"""
Example 3: Manual exception summarization
Programmatically create summaries without automatic emission.
"""

import errzip
import json

print("Example: Manual exception summarization\n")

# Create various exceptions and analyze them
test_cases = [
    ("KeyError", lambda: {}["missing"]),
    ("FileNotFoundError", lambda: open("/no/such/file.txt")),
    ("TypeError", lambda: len(42)),
    ("ValueError", lambda: int("not-a-number")),
    ("AttributeError", lambda: None.some_method()),
]

for error_name, trigger_func in test_cases:
    print(f"\n{'='*60}")
    print(f"Testing: {error_name}")
    print('='*60)

    try:
        trigger_func()
    except Exception as e:
        # Create summary manually
        summary = errzip.summarize_exception(e)

        # Display structured information
        print(f"Error Type: {summary.error_type}")
        print(f"Message: {summary.message}")
        print(f"Location: {summary.top_frame.file}:{summary.top_frame.line}")
        print(f"Function: {summary.top_frame.function}")
        print(f"Likely Cause: {summary.likely_cause}")
        print(f"Suggestions:")
        for suggestion in summary.suggestions:
            print(f"  - {suggestion}")

        # Could also serialize to JSON for logging
        # summary_json = json.dumps(errzip.asdict(summary), indent=2)

print("\n" + "="*60)
print("All tests complete")
