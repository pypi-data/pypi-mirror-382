"""Expression evaluation functionality for Norvelang interpreter."""

import ast
import inspect
import math
from lark import Tree, Token
from .safe_funcs import SAFE_FUNCS
from ..token_utils import normalize_token, check_token_in_iterable
from .utils import extract_arg_value
from ..error.exceptions import (
    DivisionByZeroError,
    FunctionError,
    ComputationOverflowError,
)


def _find_alias_match(alias: str, column: str, row: dict):
    """Find a matching aliased column in the row data."""
    for key in row.keys():
        if "." not in key:
            continue

        key_table, key_column = key.rsplit(".", 1)
        if key_column != column:
            continue

        # Check if the table part could match the alias
        if key_table.lower().startswith(alias.lower()) or check_token_in_iterable(
            alias.lower(), key_table.lower()
        ):
            v = row.get(key)
            if v != "" and v is not None:
                return v
    return None


def _handle_qualified_variable_lookup(var_name: str, row: dict):
    """Handle qualified variable references and table alias lookups."""
    # Handle qualified variable references like $countries.name
    if var_name.startswith("$") and "." in var_name:
        # Transform $countries.name to countries.name
        qualified_name = var_name[1:]  # Remove the $
        v = row.get(qualified_name)
        if v != "" and v is not None:
            return v
        return None

    # Handle table alias qualified names like c.continent
    if "." in var_name and not var_name.startswith("$"):
        alias, column = var_name.split(".", 1)

        # Ensure alias and column are strings, not tokens
        alias = normalize_token(alias)
        column = normalize_token(column)

        # Try to find matching qualified column in row
        return _find_alias_match(alias, column, row)

    return None


def extract_simple_var_name(arg):
    """Extract a simple variable name from an expression argument."""
    if hasattr(arg, "name"):
        var_name = arg.name
        # Handle qualified names like u.age -> age
        if "." in var_name:
            return var_name.split(".", 1)[1]  # Return just the column part
        return var_name

    # Use shared argument extraction utility
    return extract_arg_value(arg)


def _process_string_token(token_value):
    """Process string token by removing quotes."""
    val = normalize_token(token_value)
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    return val


def _process_number_token(token_value):
    """Process number token and return appropriate type."""
    normalized_value = normalize_token(token_value)
    return (
        float(normalized_value)
        if "." in str(normalized_value)
        else int(normalized_value)
    )


def _process_ident_token(token_value, row):
    """Process identifier token and look up in row."""
    v = row.get(normalize_token(token_value))
    return None if v == "" or v is None else v


def _eval_token_node(node, row):
    """Evaluate Token objects (leaf nodes from parser)."""
    token_type = getattr(node, "type", None)
    token_value = getattr(node, "value", str(node))

    # Normalize token_type to string using our efficient utility
    token_type = normalize_token(token_type) if token_type else None

    # Map token types to their processing functions
    token_processors = {
        "IDENT": lambda: _process_ident_token(token_value, row),
        "NUMBER": lambda: _process_number_token(token_value),
        "ESCAPED_STRING": lambda: _process_string_token(token_value),
        "SQUOTED_STRING": lambda: _process_string_token(token_value),
    }

    processor = token_processors.get(token_type)
    if processor:
        return processor()

    return normalize_token(token_value)


def _perform_arithmetic_operation(op_type, left, right):
    """Perform the actual arithmetic operation."""

    def safe_divide(l, r, op_str):
        if r == 0:
            raise DivisionByZeroError(f"{l} {op_str} {r}")
        return l / r if op_str == "/" else l % r

    operations = {
        "add_expr": lambda: left + right,
        "sub_expr": lambda: left - right,
        "mul_expr": lambda: left * right,
        "div_expr": lambda: safe_divide(left, right, "/"),
        "mod_expr": lambda: safe_divide(left, right, "%"),
        "pow_expr": lambda: left**right,
    }

    operation = operations.get(op_type)
    return operation() if operation else None


def _eval_arithmetic_tree_node(node, row):
    """Evaluate arithmetic tree operations."""
    # Check if this is an arithmetic operation
    arithmetic_ops = [
        "add_expr",
        "sub_expr",
        "mul_expr",
        "div_expr",
        "mod_expr",
        "pow_expr",
    ]

    if node.data not in arithmetic_ops:
        return None

    # Evaluate operands
    left = eval_expr_node(node.children[0], row)
    right = eval_expr_node(node.children[1], row)

    # Perform operation
    return _perform_arithmetic_operation(node.data, left, right)


def _eval_tree_node(node, row):
    """Evaluate Lark Tree objects that weren't transformed."""
    # Try arithmetic operations first
    result = _eval_arithmetic_tree_node(node, row)
    if result is not None:
        return result

    if node.data == "func_call":
        # Handle function calls in tree form
        func_name = node.children[0]
        # Convert Token to string if needed
        if hasattr(func_name, "value"):
            func_name = func_name.value
        elif hasattr(func_name, "__str__"):
            func_name = str(func_name)

        args = [eval_expr_node(arg, row) for arg in node.children[1:]]
        fn = SAFE_FUNCS.get(func_name)
        if not fn:
            raise RuntimeError(f"Unknown function {func_name}")
        return fn(*args)
    if node.data in ["sum_expr", "prod_expr", "power_expr", "unary_expr", "atom"]:
        # Handle intermediate expression nodes - just evaluate the first child
        if len(node.children) == 1:
            return eval_expr_node(node.children[0], row)
        # If multiple children, this should have been transformed - something went wrong
        raise RuntimeError(
            f"Untransformed expression tree: {node.data} with {len(node.children)} children"
        )

    # Fallback: if we can't handle it, try to get the first useful child
    for child in node.children:
        if (
            hasattr(child, "__name__")
            or hasattr(child, "value")
            or hasattr(child, "name")
        ):
            return eval_expr_node(child, row)
    raise RuntimeError(f"Unknown Tree node type: {node.data}")


def _eval_arithmetic_binary_op(op, l, r):
    """Evaluate arithmetic binary operations with security bounds checking."""
    if l is None or r is None:
        return None

    # Security bounds for safe computation
    max_exponent = 1000
    max_base_for_large_exponent = 1000000
    max_multiplication_factor = 10**15

    def safe_exponentiation():
        """Perform exponentiation with security checks."""
        # Check for negative exponents with integer bases (can cause precision issues)
        if isinstance(r, (int, float)) and r < 0 and abs(r) > 100:
            raise ComputationOverflowError(f"{l} ** {r}", "exponentiation")

        # Check exponent size
        if isinstance(r, (int, float)) and abs(r) > max_exponent:
            raise ComputationOverflowError(f"{l} ** {r}", "exponentiation")

        # Check base size for large exponents
        if (
            isinstance(r, (int, float))
            and abs(r) > 100
            and isinstance(l, (int, float))
            and abs(l) > max_base_for_large_exponent
        ):
            raise ComputationOverflowError(f"{l} ** {r}", "exponentiation")

        # Special case for very dangerous patterns like 9**9**9
        if (
            isinstance(l, (int, float))
            and isinstance(r, (int, float))
            and abs(l) > 2
            and abs(r) >= 100
        ):
            # Estimate the result size - if l^r would be huge, reject it
            try:
                # Rough estimate: log10(l^r) = r * log10(l)
                # Allow results up to 10^60 (60 digits) for reasonable large number support
                if abs(r) * math.log10(abs(l)) > 60:  # Result would have >60 digits
                    raise ComputationOverflowError(f"{l} ** {r}", "exponentiation")
            except (ValueError, OverflowError) as exc:
                raise ComputationOverflowError(f"{l} ** {r}", "exponentiation") from exc

        # Perform the calculation
        try:
            result = l**r
            # Check if result is too large (rough size check)
            if isinstance(result, (int, float)) and abs(result) > 10**200:
                raise ComputationOverflowError(f"{l} ** {r}", "exponentiation")
            return result
        except OverflowError as exc:
            raise ComputationOverflowError(f"{l} ** {r}", "exponentiation") from exc

    def safe_multiplication():
        """Perform multiplication with overflow checks."""
        try:
            result = l * r
            # Check for extremely large results that could consume memory
            if (
                isinstance(result, (int, float))
                and abs(result) > max_multiplication_factor
            ):
                # Allow it but warn if it's getting very large
                if abs(result) > 10**100:
                    # This is very large but Python can handle it, just limit string operations
                    pass
            return result
        except OverflowError as exc:
            raise ComputationOverflowError(f"{l} * {r}", "large_number") from exc

    operations = {
        "+": lambda: l + r,
        "-": lambda: l - r,
        "*": safe_multiplication,
        "/": lambda: (
            l / r
            if r != 0
            else (_ for _ in ()).throw(DivisionByZeroError(f"{l} / {r}"))
        ),
        "**": safe_exponentiation,
        "%": lambda: (
            l % r
            if r != 0
            else (_ for _ in ()).throw(DivisionByZeroError(f"{l} % {r}"))
        ),
    }

    operation = operations.get(op)
    return operation() if operation else None


def _eval_comparison_binary_op(op, l, r):
    """Evaluate comparison binary operations."""
    # For comparisons, we allow None values for equality checks
    if op in ["==", "!="]:
        operations = {
            "==": lambda: l == r,
            "!=": lambda: l != r,
        }
        return operations[op]() if l is not None or r is not None else None

    # For other comparisons, both values must be non-None
    if l is None or r is None:
        return None

    operations = {
        "<>": lambda: l != r,
        ">": lambda: l > r,
        "<": lambda: l < r,
        ">=": lambda: l >= r,
        "<=": lambda: l <= r,
    }

    operation = operations.get(op)
    return operation() if operation else None


def _eval_logical_binary_op(op, l, r):
    """Evaluate logical binary operations."""
    # Bitwise operations require non-None values
    if op in ["&", "|", "^"]:
        if l is None or r is None:
            return None
        operations = {
            "&": lambda: l & r,
            "|": lambda: l | r,
            "^": lambda: l ^ r,
        }
        return operations[op]()

    # Boolean operations
    operations = {
        "and": lambda: bool(l) and bool(r),
        "or": lambda: bool(l) or bool(r),
    }

    operation = operations.get(op)
    return operation() if operation else None


def _eval_binary_op_node(node, row):
    """Evaluate BinaryOp AST nodes."""
    l = eval_expr_node(node.left, row)
    r = eval_expr_node(node.right, row)
    op = node.op

    # Try arithmetic operations first
    result = _eval_arithmetic_binary_op(op, l, r)
    if result is not None:
        return result

    # Try comparison operations
    result = _eval_comparison_binary_op(op, l, r)
    if result is not None:
        return result

    # Try logical operations
    result = _eval_logical_binary_op(op, l, r)
    if result is not None:
        return result

    raise RuntimeError(f"Unknown binary operator: {op}")


def _eval_agg_func_node(node, row):
    """Evaluate AggFunc AST nodes."""
    # First, check if this is an aggregation lookup (in a grouped context)
    # Construct the aggregation key using the same logic as in backend.py
    arg_str = extract_simple_var_name(node.arg)
    agg_key = f"{node.name}({arg_str})"

    # Check if the aggregation result is available in the row
    if agg_key in row:
        return row[agg_key]

    # Also check if it's available under just the function name
    if node.name in row:
        return row[node.name]

    # If not in grouped context, check if this is a regular function call
    fn = SAFE_FUNCS.get(node.name)
    if fn:
        # This is a regular function, execute it
        arg_val = eval_expr_node(node.arg, row)
        if arg_val is None:
            return None
        try:
            return fn(arg_val)
        except (ValueError, TypeError, AttributeError):
            # Only catch basic evaluation errors, let custom errors bubble up
            return None

    # Check if it's a typo for a known function
    if node.name not in [
        "count",
        "sum",
        "avg",
        "min",
        "max",
    ]:  # Known aggregation functions
        available_funcs = list(SAFE_FUNCS.keys()) + [
            "sqrt",
            "count",
            "sum",
            "avg",
            "min",
            "max",
        ]
        raise FunctionError(node.name, "unknown function", available_funcs)

    # If we get here, it's an aggregation function but no result was computed
    return None


def _eval_var_node(node, row):
    """Evaluate variable nodes."""
    var_name = node.name

    # Try qualified variable lookup first
    qualified_result = _handle_qualified_variable_lookup(var_name, row)
    if qualified_result is not None:
        return qualified_result

    # Standard variable lookup
    v = row.get(var_name)
    return None if v == "" or v is None else v


def _eval_unary_op_node(node, row):
    """Evaluate unary operation nodes."""
    val = eval_expr_node(node.operand, row)

    operations = {
        "-": lambda: -val,
        "+": lambda: +val,
        "not": lambda: not val,
    }

    operation = operations.get(node.op)
    return operation() if operation else None


def _eval_func_call_node(node, row):
    """Evaluate function call nodes."""
    fn = SAFE_FUNCS.get(node.name)
    if not fn:
        if node.name == "sqrt":
            fn = math.sqrt
        else:
            available_funcs = list(SAFE_FUNCS.keys()) + ["sqrt"]
            raise FunctionError(node.name, "unknown function", available_funcs)

    args = [eval_expr_node(a, row) for a in node.args]

    sig = inspect.signature(fn)
    if len(sig.parameters) == 0:
        return fn()
    return fn(*args)


def _eval_between_expr_node(node, row):
    """Evaluate between expression nodes."""
    value = eval_expr_node(node.value, row)
    min_val = eval_expr_node(node.min_val, row)
    max_val = eval_expr_node(node.max_val, row)

    if value is None or min_val is None or max_val is None:
        return None
    return min_val <= value <= max_val


def _eval_ast_node_types(node, row):
    """Evaluate different AST node types."""
    node_type = type(node).__name__

    # Map node types to their evaluation functions
    node_evaluators = {
        "Literal": lambda: node.value,
        "Var": lambda: _eval_var_node(node, row),
        "AggFunc": lambda: _eval_agg_func_node(node, row),
        "BinaryOp": lambda: _eval_binary_op_node(node, row),
        "UnaryOp": lambda: _eval_unary_op_node(node, row),
        "FuncCall": lambda: _eval_func_call_node(node, row),
        "BetweenExpr": lambda: _eval_between_expr_node(node, row),
        "RangeExpr": lambda: list(range(int(node.start), int(node.end) + 1)),
    }

    evaluator = node_evaluators.get(node_type)
    if evaluator:
        return evaluator()

    raise RuntimeError(f"Unknown expr node type: {node_type}")


def eval_expr_node(node, row):
    """Evaluate an expression AST node against a data row."""
    if node is None:
        return None

    # Handle Token objects (leaf nodes from parser) - both regular lark and lark-cython
    if isinstance(node, Token) or hasattr(node, "type") and hasattr(node, "value"):
        return _eval_token_node(node, row)

    # Handle Lark Tree objects that weren't transformed
    if isinstance(node, Tree):
        return _eval_tree_node(node, row)

    if hasattr(node, "raw"):
        return eval_expr_legacy(node.raw)

    # Handle different AST node types
    return _eval_ast_node_types(node, row)


def eval_expr_legacy(expr_str):
    """Legacy string-based expression evaluation with ast.literal_eval."""
    # Special case for * in aggregate functions
    if expr_str.strip() == "*":
        return "*"  # Return the literal star for aggregate functions

    # Try ast.literal_eval for simple literals (fast and safe)
    try:
        return ast.literal_eval(expr_str)
    except (SyntaxError, ValueError, TypeError):
        # Return None for any evaluation error
        return None
