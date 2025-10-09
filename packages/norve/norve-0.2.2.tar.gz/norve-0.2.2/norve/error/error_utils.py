"""
Error handling utilities for Norvelang parser and interpreter.

This module provides functions for handling parse errors, runtime errors,
and generating helpful error messages with suggestions.
"""

import difflib
import re
from .syntax import print_syntax_error, print_runtime_error
from .exceptions import (
    DivisionByZeroError,
    ComputationOverflowError,
    FunctionError,
    FileError,
    ColumnError,
)


def handle_parse_error(block_num, block_str, msg):
    """
    Handle parser errors and generate helpful error messages.

    Args:
        block_num (int): Block number where the error occurred
        block_str (str): The code block that caused the error
        msg (str): The original parser error message
    """
    # Remove debug print
    # Parse multi-line error message for unexpected and expected tokens
    hints = []
    # Extract unexpected token
    m = re.search(r"Unexpected token Token\('([A-Z_]+)', '([^']+)'\)", msg)
    word = None
    if m:
        _, token_val = m.groups()
        word = token_val.lower()
    # Extract expected keywords (multi-line)
    expected_keywords = re.findall(r"\* ([A-Z_]+)", msg)
    # Map parser keywords to Norvelang keywords
    parser_to_lang = {
        "GROUP": "group",
        "USE": "use",
        "ORDER": "order",
        "TITLE": "title",
        "LIMIT": "limit",
        "WHERE": "where",
        "MAP": "map",
        "JOIN": "join",
        "LEFT": "left",
        "RIGHT": "right",
        "INNER": "inner",
        "FULL": "full",
        "CROSS": "cross",
        "NATURAL": "natural",
        "SAVE": "save",
        "LET": "let",
        "ON": "on",
        "JOIN_TYPE": "join",
        "JOIN_TYPE_NO_KEY": "join",
    }
    # Suggest closest expected keyword if typo
    if word and expected_keywords:
        expected_lang = [parser_to_lang.get(k, k.lower()) for k in expected_keywords]
        close = difflib.get_close_matches(word, expected_lang, n=1)
        if close:
            hints.append(f"Did you mean '{close[0]}'?")
    # If only one expected keyword and user missed it (e.g. ON)
    if "Expected one of:" in msg and len(expected_keywords) == 1:
        expected = parser_to_lang.get(
            expected_keywords[0], expected_keywords[0].lower()
        )
        hints.append(
            f"Expected '{expected}' at this position. "
            "Check for missing or misplaced keywords."
        )
    # Check for missing/extra parameter patterns
    if "Expected" in msg and "but got" in msg:
        m2 = re.search(r"Expected (.*?) but got (.*?)$", msg)
        if m2:
            expected, got = m2.groups()
            hints.append(
                f"Expected {expected}, but got {got}. "
                "Check for missing or extra parameters."
            )
    # Check for common join/step mistakes
    if "join" in block_str and "on" not in block_str:
        hints.append(
            "Join statements usually require an 'on' clause, e.g. join ... on ..."
        )
    if "group" in block_str and "by" not in block_str and "group" in msg:
        hints.append(
            "Did you mean 'group'? (Norvelang uses 'group' without 'by', "
            "but check your syntax)"
        )
    if hints:
        print_syntax_error(block_num, block_str, suggestion=hints)
    else:
        print_syntax_error(block_num, block_str)


def _get_division_error_hints():
    """Get hints for division by zero errors."""
    return [
        "Check that denominator values are not zero",
        "Use conditional logic to avoid division by zero",
        "Consider using CASE/WHEN or WHERE clauses to filter out zero values"
    ]


def _get_function_error_hints(exception, available_functions):
    """Get hints for function errors."""
    hints = []
    func_name = getattr(exception, "function_name", "")

    if func_name and available_functions:
        close_matches = difflib.get_close_matches(
            func_name, available_functions, n=1, cutoff=0.6
        )
        if close_matches:
            hints.append(f"Did you mean '{close_matches[0]}'?")

    # Add available functions hint (show common ones)
    if available_functions:
        common_funcs = ["upper", "lower", "len", "sum", "count", "avg", "max", "min"]
        available = [f for f in common_funcs if f in available_functions]
        if available:
            hints.append(f"Common functions: {', '.join(available[:6])}")
        else:
            # Show first few available functions
            hints.append(
                f"Available functions: {', '.join(sorted(available_functions)[:8])}"
            )
    return hints


def _get_file_error_hints():
    """Get hints for file errors."""
    return [
        "Check that the file path is correct",
        "Ensure the file exists and is readable"
    ]


def _get_column_error_hints():
    """Get hints for column errors."""
    return [
        "Check column names for typos",
        "Use 'use' without arguments to see available columns"
    ]


def handle_runtime_error(exception, block_num, block_str):
    """
    Handle runtime errors and provide helpful suggestions.

    Args:
        exception: The exception that was raised
        block_num (int): Block number where the error occurred
        block_str (str): The code block that caused the error
    """
    error_msg = str(exception)
    hints = []

    if isinstance(exception, (DivisionByZeroError, ZeroDivisionError)):
        hints.extend(_get_division_error_hints())
    elif isinstance(exception, ComputationOverflowError):
        # Get hints from the exception's suggestions
        if hasattr(exception, "suggestions"):
            hints.extend(exception.suggestions)
    elif isinstance(exception, FunctionError):
        available_functions = getattr(exception, "available_functions", [])
        hints.extend(_get_function_error_hints(exception, available_functions))
    elif isinstance(exception, (FileError, FileNotFoundError)):
        hints.extend(_get_file_error_hints())
    elif isinstance(exception, ColumnError):
        hints.extend(_get_column_error_hints())

    # Print the error in block format
    print_runtime_error(error_msg, block_num, block_str)

    # Print hints
    if hints:
        for hint in hints:
            yellow = "\033[93m"
            reset = "\033[0m"
            print(f"{yellow}Hint: {hint}{reset}")
    print()
