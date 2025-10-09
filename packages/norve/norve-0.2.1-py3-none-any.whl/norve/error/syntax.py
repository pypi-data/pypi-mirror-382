"""
Syntax error printing utilities for Norvelang.

This module provides functions for printing formatted error messages
with color-coded output for better readability.
"""

# ANSI color codes for terminal output
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_syntax_error(block_num, block_str, suggestion=None):
    """
    Print a formatted syntax error message.
    
    Args:
        block_num (int): Block number where the error occurred
        block_str (str): The code block that caused the error
        suggestion (str|list, optional): Suggestions for fixing the error
    """
    print(f"{RED}Syntax error in block {block_num}:{RESET}")
    print(f"{block_str}")
    if suggestion:
        # Always print a label for the hint
        if isinstance(suggestion, str):
            print(f"{YELLOW}Hint: {suggestion}{RESET}\n")
        elif isinstance(suggestion, (list, tuple)):
            for s in suggestion:
                print(f"{YELLOW}Hint: {s}{RESET}\n")


def print_runtime_error(msg, block_num=None, block_str=None):
    """
    Print a formatted runtime error message.
    
    Args:
        msg (str): The error message
        block_num (int, optional): Block number where the error occurred
        block_str (str, optional): The code block that caused the error
    """
    if block_num is not None:
        print(f"{RED}Runtime error in block {block_num}:{RESET}")
        if block_str:
            print(f"{block_str}")
        print(f"{RED}{msg}{RESET}")
    else:
        print(f"{RED}Runtime error:{RESET}")
        print(f"{RED}{msg}{RESET}")


def print_any_error():
    """Print a general error message indicating that some blocks had errors."""
    print(f"{YELLOW}Some blocks had errors. Please fix them and try again.{RESET}")
