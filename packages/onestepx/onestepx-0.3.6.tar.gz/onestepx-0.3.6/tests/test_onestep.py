from onestepx import collapse_to_terminal, TERMINAL
from onestepx.hierarchy import Node, traverse

def test_collapse_to_terminal_identity():
    root = Node("Root")
    root.add_child(Node("Child"))
    assert collapse_to_terminal(root) is TERMINAL

def test_traverse_returns_identity_set():
    a = Node("A")
    b = Node("B")
    c = Node("C")
    a.add_child(b); b.add_child(c)
    seen = traverse(a)
    assert a in seen and b in seen and c in seen
