"""Norvelang - Multi-Source Data Processing Language."""
from .parser import parse
from .api import execute, execute_query, execute_with_output, NorvelangResult

# Make the library functions available at the top level
__all__ = [
    "parse",
    "execute",
    "execute_query",
    "execute_with_output",
    "NorvelangResult",
]
