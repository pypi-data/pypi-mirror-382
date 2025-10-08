from __future__ import annotations
from .core import collapse_to_terminal, TERMINAL
from .hierarchy import Node

def main() -> None:
    # tiny demo
    root = Node("Root")
    root.add_child(Node("Child"))
    t = collapse_to_terminal(root)
    print("Collapsed:", t is TERMINAL and "Terminal" or t)
