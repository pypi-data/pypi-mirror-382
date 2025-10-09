"""
Utilities for the Norvelang API.

This module contains helper functions and context managers used by the API.
"""

import sys
import io
from contextlib import contextmanager


@contextmanager
def capture_stdout():
    """Context manager to capture stdout as a string."""
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        yield buffer
    finally:
        sys.stdout = old_stdout


def filter_empty_blocks(blocks):
    """
    Filter empty blocks from a list, returning non-empty blocks with their indices.

    Args:
        blocks: List of code blocks

    Yields:
        Tuple of (index, block_string) for each non-empty block
    """
    for i, block in enumerate(blocks):
        block_str = block.strip()
        if not block_str:
            continue
        yield i, block_str


def process_column_selection(
    columns,
    rows_to_show,
    expand_wildcard_columns_func,
    evaluate_column_expression_func,
    extract_col_name_func,
):
    """
    Process column selection and evaluation for rows.

    This function handles the common logic for processing columns:
    1. Expanding wildcard columns
    2. Building column names with aliases
    3. Processing each row and evaluating column expressions
    4. Ensuring all requested columns are present

    Args:
        columns: List of (col_expr, alias) tuples
        rows_to_show: List of row dictionaries
        expand_wildcard_columns_func: Function to expand wildcard columns
        evaluate_column_expression_func: Function to evaluate column expressions
        extract_col_name_func: Function to extract column names

    Returns:
        Tuple of (out_rows, col_names) where out_rows is list of processed row dicts
        and col_names is list of column names
    """
    # Expand wildcard columns
    columns = expand_wildcard_columns_func(columns, rows_to_show)

    # Process column selection
    out_rows = []
    col_names = []

    # Build column names first
    for col_expr, alias in columns:
        if alias is not None and alias != "None":
            col_names.append(str(alias))
        else:
            col_name = extract_col_name_func(col_expr)
            if not col_name or col_name == "None":
                col_name = str(col_expr)
            col_names.append(str(col_name))

    # Process each row
    for r in rows_to_show:
        out_row = {}
        row_keys = list(r.keys())

        for col_expr, alias in columns:
            col_name, val = evaluate_column_expression_func(
                col_expr, alias, r, row_keys
            )
            out_row[col_name] = val

        # Ensure all requested columns are present in the row
        for cname in col_names:
            if cname not in out_row:
                out_row[cname] = None
        out_rows.append(out_row)

    return out_rows, col_names
