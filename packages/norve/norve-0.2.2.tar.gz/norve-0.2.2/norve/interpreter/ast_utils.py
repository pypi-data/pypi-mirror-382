"""Utilities for working with AST nodes in the interpreter."""

from ..ast.agg import AggFunc


def find_agg_funcs(expr):
    """Iterative traversal to collect AggFunc nodes from expression AST."""
    agg_funcs = []
    stack = [expr]
    while stack:
        node = stack.pop()
        if isinstance(node, AggFunc):
            agg_funcs.append(node)
            continue
        # Common AST shapes
        # BinaryOps have left/right
        left = getattr(node, "left", None)
        right = getattr(node, "right", None)
        if left is not None or right is not None:
            if left is not None:
                stack.append(left)
            if right is not None:
                stack.append(right)
            continue
        operand = getattr(node, "operand", None)
        if operand is not None:
            stack.append(operand)
            continue
        args = getattr(node, "args", None)
        if args:
            stack.extend(args)
            continue
        children = getattr(node, "children", None)
        if children:
            stack.extend(children)

    return agg_funcs
