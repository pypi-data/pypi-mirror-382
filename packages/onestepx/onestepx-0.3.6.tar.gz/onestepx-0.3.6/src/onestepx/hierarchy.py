"""Lightweight node type and utilities."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(eq=False)
class Node:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'flags'):
            self.flags = {}  # ensure .flags always exists
    name: str
    ordinal: object | None = None
    children: list["Node"] = field(default_factory=list)

    def add_child(self, node: "Node") -> None:
        self.children.append(node)

    def __repr__(self) -> str:
        return f"Node({self.name})"

def traverse(node: Node, visited: set[Node] | None = None) -> set[Node]:
    """DFS traversal returning identity-set of visited nodes.

    Uses object identity (hash by id) due to eq=False in dataclass.
    """
    if visited is None:
        visited = set()
    if node in visited:
        return visited
    visited.add(node)
    for child in node.children:
        traverse(child, visited)
    return visited

# --- Global safety patch for external imports (drivers/tests) ---
_orig_init = Node.__init__
def _patched_init(self, *a, **kw):
    _orig_init(self, *a, **kw)
    if not hasattr(self, "flags"):
        self.flags = {}
Node.__init__ = _patched_init
# ----------------------------------------------------------------

