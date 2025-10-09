"""
Utility functions for the interpreter package.

This module contains shared utility functions used by interpreter modules,
separated to avoid cyclic import issues.
"""


def extract_arg_value(arg):
    """
    Extract value from argument that may have various attributes.
    
    Common utility for extracting simple values from arguments that may
    have 'raw', 'value', or other attributes.
    
    Args:
        arg: Argument object with potential attributes
        
    Returns:
        String value extracted from the argument
    """
    if hasattr(arg, "raw"):
        return arg.raw
    if hasattr(arg, "value"):
        return str(arg.value)
    return str(arg)
