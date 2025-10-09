"""
Expression transformers for AST transformation.

This module contains transformers for expressions like binary operations, literals, variables, etc.
"""

from ..ast.expr import Literal, Var, BinaryOp, UnaryOp, FuncCall, RangeExpr, BetweenExpr
from ..token_utils import normalize_token


class ExpressionTransformers:
    """Mixin class for expression transformation methods."""

    def _normalize_token(self, token):
        """Normalize a token to string, handling both lark and lark-cython tokens."""
        return normalize_token(token)

    def number(self, items):
        """Transform number literal."""
        token = items[0]
        if hasattr(token, "value"):
            value = token.value
        else:
            value = token

        # Try to parse as int first, then float
        try:
            if "." in str(value) or "e" in str(value).lower():
                return Literal(float(value))
            return Literal(int(value))
        except ValueError:
            return Literal(float(value))

    def string(self, items):
        """Transform string literal."""
        return Literal(items[0])

    def var(self, items):
        """Transform variable reference."""
        # items[0] is the variable name token or dotted identifier
        if len(items) == 1:
            item = items[0]
            if hasattr(item, "children"):
                # Handle dotted identifiers
                name = ".".join(str(child) for child in item.children)
            else:
                name = self._normalize_token(item)
            return Var(name)
        # Multiple parts - join with dots
        parts = []
        for item in items:
            parts.append(self._normalize_token(item))
        return Var(".".join(parts))

    def func_call(self, items):
        """Transform function call."""
        func_name = self._normalize_token(items[0])

        args = items[1] if len(items) > 1 else []
        return FuncCall(func_name, args)

    def expr_list(self, items):
        """Transform expression list."""
        return items

    def range(self, items):
        """Transform range expression."""
        # items should be [start, end] or [start, end, step]
        start = items[0]
        end = items[1]
        step = items[2] if len(items) > 2 else None
        return RangeExpr(start, end, step)

    def unary_op(self, items):
        """Transform unary operation."""
        # items[0] is the operator, items[1] is the operand
        op = items[0]
        if hasattr(op, "value"):
            op = op.value
        operand = items[1]
        return UnaryOp(op, operand)

    def not_op(self, items):
        """Transform NOT operation."""
        # items[0] is the operand (comp_expr)
        operand = items[0]
        return UnaryOp("not", operand)

    def or_expr(self, items):
        """Transform OR expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="or", left=items[0], right=items[1])

    def and_expr(self, items):
        """Transform AND expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="and", left=items[0], right=items[1])

    def comp_expr(self, items):
        """Transform comparison expression."""
        if len(items) == 1:
            return items[0]
        # items[0] is left expr, items[1] is operator, items[2] is right expr
        return BinaryOp(op=items[1], left=items[0], right=items[2])

    def between_expr(self, items):
        """Transform BETWEEN expression."""
        # items[0] is value, items[1] is min_val, items[2] is max_val
        # "value between min_val and max_val"
        return BetweenExpr(value=items[0], min_val=items[1], max_val=items[2])

    def add_expr(self, items):
        """Transform addition expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="+", left=items[0], right=items[1])

    def sub_expr(self, items):
        """Transform subtraction expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="-", left=items[0], right=items[1])

    def mul_expr(self, items):
        """Transform multiplication expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="*", left=items[0], right=items[1])

    def div_expr(self, items):
        """Transform division expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="/", left=items[0], right=items[1])

    def mod_expr(self, items):
        """Transform modulo expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="%", left=items[0], right=items[1])

    def pow_expr(self, items):
        """Transform power expression."""
        if len(items) == 1:
            return items[0]
        return BinaryOp(op="**", left=items[0], right=items[1])
