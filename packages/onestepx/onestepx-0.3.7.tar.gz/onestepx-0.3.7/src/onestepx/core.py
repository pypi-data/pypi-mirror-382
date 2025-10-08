"""Core OneStep operations."""
from __future__ import annotations
from .hierarchy import Node

# Single shared terminal node
TERMINAL = Node("Terminal")

def collapse_to_terminal(node: Node) -> Node:
    """Return the terminal object for any input hierarchy.

    Complexity: O(1)
    The semantics match the OneStep model: queries operate on TERMINAL, not the input graph.
    """
    return TERMINAL
