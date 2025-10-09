"""
Transformer package for norvelang AST transformation.

This package provides AST transformation split into focused modules:
- core: Main ASTTransformer class
- statements: Statement transformation methods
- expressions: Expression transformation methods
- pipelines: Pipeline and data source transformation methods
"""

from .core import ASTTransformer

__all__ = ["ASTTransformer"]
