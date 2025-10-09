"""Clipboard utilities."""

import pyperclip
from typing import Optional


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard.
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def get_clipboard_text() -> Optional[str]:
    """
    Get text from clipboard.
    
    Returns:
        Clipboard text or None if failed
    """
    try:
        return pyperclip.paste()
    except Exception:
        return None


def is_clipboard_available() -> bool:
    """
    Check if clipboard is available.
    
    Returns:
        True if clipboard is available, False otherwise
    """
    try:
        # Try to copy and paste a test string
        test_text = "clipboard_test"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        return result == test_text
    except Exception:
        return False
