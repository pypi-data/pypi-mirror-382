"""Pipeline execution utilities for Norvelang."""

import json
import os
import sqlite3
import traceback
import pandas as pd
from lark import LarkError

from .ast import Let
from .ast.steps import Title
from .interpreter import execute_pipeline
from .error.error_utils import handle_parse_error, handle_runtime_error
from .error.block_split import split_blocks
from .error.syntax import print_any_error
from .error.exceptions import NorvelangError
from .api.utils import filter_empty_blocks
from .parser import parse


class TableIndexManager:
    """Manages table index counter for pipeline execution."""

    def __init__(self):
        self.index = 0

    def next_index(self):
        """Get the next table index."""
        self.index += 1
        return self.index

    def reset(self):
        """Reset the table index counter."""
        self.index = 0


# Global table index manager instance
_table_manager = TableIndexManager()


def _load_file_data(path, pipe_name):
    """Load data from a file based on its extension."""
    ext = os.path.splitext(path)[1].lower()
    conn = None
    data = []

    try:
        if ext == ".csv":
            data = pd.read_csv(path).to_dict(orient="records")
        elif ext in (".xlsx", ".xls"):
            data = pd.read_excel(path).to_dict(orient="records")
        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                data = json_data if isinstance(json_data, list) else [json_data]
        elif ext in (".sqlite", ".sqlite3", ".db"):
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            if tables:
                cur.execute(f"SELECT * FROM {tables[0]}")
                cols = [desc[0] for desc in cur.description]
                data = [dict(zip(cols, row)) for row in cur.fetchall()]
        # For unsupported extensions, data remains []

    except (
        FileNotFoundError,
        OSError,
        pd.errors.ParserError,
        json.JSONDecodeError,
        sqlite3.Error,
    ) as e:
        print(f"Failed to load file '{path}' for let '{pipe_name}': {e}")
        data = []
    finally:
        if conn:
            conn.close()

    return data


def _handle_let_statement(pipe, let_tables, default_limit):
    """Handle let statement execution."""
    pipeline_val = pipe.pipeline

    # Handle 'let x = null' to remove variable
    if (
        (isinstance(pipeline_val, str) and pipeline_val.strip().lower() == "null")
        or getattr(pipeline_val, "value", None) is None
        and str(pipeline_val).strip().lower() == "null"
    ):
        let_tables.pop(pipe.name, None)
        return False

    if pipeline_val == "rows":
        return False

    # If the right-hand side is a string and looks like a file path, load the file
    if isinstance(pipeline_val, str) and pipeline_val.lower().endswith(
        (".csv", ".json", ".xlsx", ".xls", ".sqlite", ".sqlite3", ".db")
    ):
        let_tables[pipe.name] = _load_file_data(pipeline_val, pipe.name)
        return False

    # Otherwise, execute as pipeline (silently for let statements)
    let_tables[pipe.name] = execute_pipeline(
        pipeline_val, let_tables, default_limit=default_limit, silent=True
    )
    return False


def _handle_pipeline_with_title(pipe, let_tables, default_limit):
    """Handle pipeline execution with title printing."""
    # Print the title if present, or a default if missing
    found_title = False
    for step in pipe.steps:
        if isinstance(step, Title):
            print(f"\n=== {step.text} ===")
            found_title = True
            break
    if not found_title:
        table_index = _table_manager.next_index()
        print(f"\n=== Table {table_index} ===")

    execute_pipeline(pipe, let_tables, default_limit=default_limit)
    return True


def _handle_parse_error(block_num, block_str, error, show_internal_errors):
    """Handle parsing errors for a block."""
    handle_parse_error(block_num, f"\033[90m{block_str}\033[0m", str(error))
    if show_internal_errors:
        print("Internal error details:")
        traceback.print_exc()


def _handle_runtime_error(block_num, block_str, error, show_internal_errors):
    """Handle runtime errors for a block."""
    handle_runtime_error(block_num, block_str, error)
    if show_internal_errors:
        print("Internal error details:")
        traceback.print_exc()


def _execute_ast(ast, let_tables, default_limit):
    """Execute parsed AST."""
    if isinstance(ast, list):
        for pipe in ast:
            run_pipe(pipe, let_tables, default_limit)
    else:
        run_pipe(ast, let_tables, default_limit)


def run_pipeline(
    pipeline,
    let_tables=None,
    default_limit=10,
    show_internal_errors=None,
    use_cython=True,
):
    """Parse and execute a norvelang pipeline string."""
    if let_tables is None:
        let_tables = {}

    blocks = split_blocks(pipeline)
    any_error = False

    for i, block_str in filter_empty_blocks(blocks):
        # Parse block
        try:
            ast = parse(block_str, use_cython=use_cython)
        except (LarkError, NorvelangError) as e:
            _handle_parse_error(i + 1, block_str, e, show_internal_errors)
            any_error = True
            continue

        # Execute block
        try:
            _execute_ast(ast, let_tables, default_limit)
        except (NorvelangError, ValueError, TypeError, KeyError, AttributeError) as e:
            _handle_runtime_error(i + 1, block_str, e, show_internal_errors)
            any_error = True

    if any_error:
        print_any_error()


def run_pipe(pipe, let_tables, default_limit):
    """
    Execute a single pipeline or let statement.

    Args:
        pipe: The AST node to execute (Let or Pipeline)
        let_tables: Dictionary of stored variables
        default_limit: Default row limit for results

    Returns:
        bool: True if output was displayed, False otherwise
    """
    if isinstance(pipe, Let):
        return _handle_let_statement(pipe, let_tables, default_limit)

    if hasattr(pipe, "steps"):
        return _handle_pipeline_with_title(pipe, let_tables, default_limit)

    raise RuntimeError(f"Unknown top-level statement: {pipe}")
