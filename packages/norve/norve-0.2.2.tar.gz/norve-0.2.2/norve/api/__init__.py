"""
Norvelang API package initialization.
"""

from .core import execute_query, execute_with_output, execute
from .result_types import NorvelangResult
from .utils import capture_stdout

__all__ = [
    "execute_query",
    "execute_with_output",
    "execute",
    "NorvelangResult",
    "capture_stdout",
]
