"""
DataFrame capture functionality for the Norvelang API.

This module contains the logic for intercepting use() calls and converting them to DataFrames
while preserving all column filtering and expression evaluation.
"""

from typing import List
import pandas as pd
from lark import Token
from ..interpreter.backend.display import process_columns_with_display_funcs


class DataFrameCapture:
    """Helper class for capturing DataFrames from use() operations."""

    def __init__(self):
        self.captured_dfs: List[pd.DataFrame] = []

    def create_capture_use_method(self):
        """Create a replacement use method that captures DataFrames."""

        def capture_use(self, columns=None, limit=None):
            """Replacement use method that captures DataFrames instead of printing."""
            # Apply limit first
            n = limit if limit is not None else getattr(self, "_default_limit", None)
            if n is None:
                n = len(self.rows) if self.rows else 0
            rows_to_show = self.rows[:n]

            if not rows_to_show:
                capture_use.captured_dfs.append(pd.DataFrame())
                return self

            # Handle None columns case - show everything
            if columns is None:
                columns = [(Token("STAR", "*"), None)]

            # Use the same logic as the original use method
            # Process column selection using shared utility
            out_rows, _ = process_columns_with_display_funcs(
                columns,
                rows_to_show,
            )

            # Create DataFrame with the filtered columns
            df = pd.DataFrame(out_rows)
            capture_use.captured_dfs.append(df)
            return self

        # Bind the capture instance to the method
        capture_use.captured_dfs = self.captured_dfs
        return capture_use

    def get_dataframes(self):
        """Get all captured DataFrames."""
        return self.captured_dfs.copy()

    def clear(self):
        """Clear all captured DataFrames."""
        self.captured_dfs.clear()

    def get_count(self):
        """Get the number of captured DataFrames."""
        return len(self.captured_dfs)
