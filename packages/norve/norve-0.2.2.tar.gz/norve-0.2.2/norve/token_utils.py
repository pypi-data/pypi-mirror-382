"""
Token utilities for handling both regular lark and lark-cython tokens efficiently.

This module provides centralized token normalization and debugging capabilities
based on the parser's cython usage configuration.
"""

from typing import Union, Any
from lark import Token


def strip_quotes(text: str) -> str:
    """Remove surrounding quotes from a string."""
    if len(text) >= 2 and text[0] in ('"', "'") and text[-1] == text[0]:
        return text[1:-1]
    return text


def normalize_token(token: Union[str, Any]) -> str:
    """
    Efficiently normalize a token to string for both lark and lark-cython.
    """
    if isinstance(token, str):
        return token
    if isinstance(token, Token):
        return token.value
    if hasattr(token, "value"):
        return token.value
    return str(token)


def debug_token(token: Any, context: str = "") -> str:
    """
    Debug token information for troubleshooting.
    """
    token_type = type(token).__name__
    module = getattr(type(token), "__module__", "unknown")
    debug_info = f"DEBUG {context}: {token_type} from {module}"
    if hasattr(token, "type"):
        debug_info += f", type={getattr(token, 'type', 'None')}"
    if hasattr(token, "value"):
        debug_info += f", value={getattr(token, 'value', 'None')}"
    debug_info += f", str={str(token)}"
    return debug_info


def is_token_object(obj: Any) -> bool:
    """
    Check if an object is a token (lark or lark-cython).
    """
    return isinstance(obj, Token) or hasattr(obj, "type") and hasattr(obj, "value")


def safe_string_operation(obj: Any, operation: str, *args, **kwargs) -> Any:
    """
    Safely perform string operations on tokens or strings.
    """
    obj_str = normalize_token(obj)
    return getattr(obj_str, operation)(*args, **kwargs)


def check_token_in_iterable(token: Any, iterable: Any) -> bool:
    """
    Safely check if a token is in an iterable, handling token normalization.
    """
    normalized = normalize_token(token)
    return normalized in iterable
