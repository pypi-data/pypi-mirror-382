"""AST nodes for expressions in Norvelang."""
from dataclasses import dataclass
from typing import List, Any


@dataclass
class Expr:
    """Base class for all expression AST nodes."""


@dataclass
class Literal(Expr):
    """Literal value expression."""
    value: Any


@dataclass
class Var(Expr):
    """Variable reference expression."""
    name: str


@dataclass
class BinaryOp(Expr):
    """Binary operation expression (e.g., +, -, *, /, ==, !=)."""
    op: str
    left: Expr
    right: Expr


@dataclass
class UnaryOp(Expr):
    """Unary operation expression (e.g., -, not)."""
    op: str
    operand: Expr


@dataclass
class FuncCall(Expr):
    """Function call expression."""
    name: str
    args: List[Expr]


@dataclass
class RangeExpr(Expr):
    """Range expression (start..end or start..end..step)."""
    start: Any
    end: Any
    step: Any = None


@dataclass
class BetweenExpr(Expr):
    """Between expression (value between min_val and max_val)."""
    value: Expr
    min_val: Expr
    max_val: Expr


@dataclass
class RawExpr(Expr):
    """Raw expression with unparsed string content."""
    raw: str
