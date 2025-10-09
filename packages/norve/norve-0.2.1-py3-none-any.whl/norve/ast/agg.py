"""AST nodes for aggregation functions in Norvelang."""
from dataclasses import dataclass
from typing import Optional
from .expr import Expr


@dataclass
class AggFunc:
    """Aggregation function AST node."""
    name: str
    arg: Optional[Expr]  # None or RawExpr '*' or expression
