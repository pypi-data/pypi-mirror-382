"""
Example 1: Basic exception hook usage
Install global hook to catch all unhandled exceptions.
"""

import errzip

# Install the global exception hook
errzip.install_excepthook()

print("errzip hook installed. Triggering exceptions...")

# Example 1: KeyError
print("\n1. KeyError example:")
data = {"foo": "bar"}
result = data["missing_key"]  # This will trigger errzip analysis
