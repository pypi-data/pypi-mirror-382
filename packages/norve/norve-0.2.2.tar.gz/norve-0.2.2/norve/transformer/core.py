"""
Core AST transformer that combines all transformation mixins.

This module provides the main ASTTransformer class that inherits from all
the specialized transformer mixins.
"""

from lark import Transformer

from .statements import StatementTransformers
from .expressions import ExpressionTransformers
from .pipelines import PipelineTransformers


class ASTTransformer(Transformer):
    """Transform Lark parse trees into norvelang AST nodes.

    This class combines all the specialized transformer mixins to provide
    a complete transformation capability for the norvelang AST.

    Uses composition instead of multiple inheritance to avoid deep inheritance chains.
    Note: This class primarily serves as a composition container and dynamically
    adds methods from component transformers, so the too-few-public-methods warning
    is not applicable here.
    """

    def __init__(self):
        super().__init__()
        # Use composition instead of inheritance to reduce ancestor count
        self._statement_transformer = StatementTransformers()
        self._expression_transformer = ExpressionTransformers()
        self._pipeline_transformer = PipelineTransformers()

        # Dynamically add methods from all transformers
        self._add_transformer_methods(self._statement_transformer)
        self._add_transformer_methods(self._expression_transformer)
        self._add_transformer_methods(self._pipeline_transformer)

    def _add_transformer_methods(self, transformer):
        """Add methods from a transformer to this class."""
        for method_name in dir(transformer):
            if (not method_name.startswith('_') and
                callable(getattr(transformer, method_name)) and
                not hasattr(self, method_name)):
                # Bind the method to this instance
                method = getattr(transformer, method_name)
                setattr(self, method_name, method)

    def get_transformers(self):
        """Get list of component transformers for debugging."""
        return [
            self._statement_transformer,
            self._expression_transformer,
            self._pipeline_transformer
        ]
