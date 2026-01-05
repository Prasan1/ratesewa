"""
Text formatting utilities for RankSewa
Handles proper capitalization and formatting of user-entered text
"""

def normalize_name(name):
    """
    Normalize a person's name to proper Title Case

    Handles:
    - ALL UPPERCASE → Title Case
    - all lowercase → Title Case
    - MiXeD cAsE → Title Case
    - Preserves "Dr. " prefix

    Examples:
        "ASHWINI GURUNG" → "Ashwini Gurung"
        "DR. RAM PRASAD" → "Dr. Ram Prasad"
        "john doe" → "John Doe"
        "Dr. SITA KUMARI" → "Dr. Sita Kumari"

    Args:
        name (str): The name to normalize

    Returns:
        str: Properly formatted name
    """
    if not name:
        return name

    name = name.strip()

    if not name:
        return name

    # Handle Dr. prefix
    prefix = ""
    name_part = name

    # Check for various Dr. prefixes (case insensitive)
    if name.lower().startswith("dr. "):
        prefix = "Dr. "
        name_part = name[4:]
    elif name.lower().startswith("dr "):
        prefix = "Dr. "
        name_part = name[3:]

    # Convert to title case
    name_part = name_part.title()

    # Handle special cases for names
    # (Optional: Add more special cases as needed for Nepali names)
    # Example: "Mcdonald" → "McDonald"

    return prefix + name_part


def normalize_text(text, preserve_case=False):
    """
    Normalize general text input

    Args:
        text (str): Text to normalize
        preserve_case (bool): If True, preserve existing case

    Returns:
        str: Normalized text
    """
    if not text:
        return text

    text = text.strip()

    # Remove multiple spaces
    text = ' '.join(text.split())

    if not preserve_case and text.isupper() and len(text) > 2:
        # If text is all uppercase, convert to sentence case
        text = text.capitalize()

    return text
