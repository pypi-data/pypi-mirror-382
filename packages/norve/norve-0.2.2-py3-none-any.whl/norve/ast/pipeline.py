"""AST node for pipelines in Norvelang."""
from dataclasses import dataclass
from typing import List
from .steps import Step


@dataclass
class Pipeline:
    """A pipeline consisting of a sequence of processing steps."""
    steps: List[Step]

    def __repr__(self):
        steps_repr = ",\n  ".join(repr(step) for step in self.steps)
        return f"Pipeline([\n  {steps_repr}\n])"
