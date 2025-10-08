"""OneStepX public API (safe, no monkeypatch)."""

__version__ = "0.3.7"

from .hierarchy import Node
from .core import TERMINAL, collapse_to_terminal
from .runtime import ensure_collapsed, collapse_hash
from .expr import compile_expr
from .temporal import between, sum_by, avg_by, median_by
from .ordinals import *

# Ensure TERMINAL.flags always exists for drivers/tests.
if not hasattr(TERMINAL, "flags"):
    TERMINAL.flags = {}

__all__ = [
    "Node", "TERMINAL", "collapse_to_terminal",
    "ensure_collapsed", "collapse_hash",
    "compile_expr", "between", "sum_by", "avg_by", "median_by"
]
