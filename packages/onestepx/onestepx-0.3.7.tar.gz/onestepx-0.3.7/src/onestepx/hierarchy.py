"""Lightweight node type and utilities."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(eq=False)
class Node:
    def __init__(self, name: str, children=None):
        self.name = name
        self.children = []
        if children:
            for ch in children:
                self.add_child(ch)

    def add_child(self, node: "Node") -> None:
        self.children.append(node)

    def traverse(self):
        yield self
        for ch in self.children:
            yield from ch.traverse()

    def __repr__(self):
        return f"Node({self.name})"


# --- module-level helper for tests ---
def traverse(root: "Node"):
    """Yield nodes in pre-order starting from root."""
    if hasattr(root, "traverse"):
        yield from root.traverse()
    else:
        yield root
