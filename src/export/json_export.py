"""
JSON export helper.
Converts the current state data to a structured, pretty-printed JSON string.
"""

from src.state import export_to_json

def generate_json():
    """Return the current session state as a formatted JSON string."""
    return export_to_json()
