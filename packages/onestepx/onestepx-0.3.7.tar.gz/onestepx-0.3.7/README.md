# OneStep

Instant hierarchical collapse — from O(N) traversal to O(1) constant time.

---

## What is it?

**OneStep** implements the OneStep search model: pre‑collapse any hierarchy to a single terminal representation `T` so that predicates operate on `T` instead of traversing nodes.

Formally, for a predicate `P` over nodes, OneStep defines a lifted predicate
`P^#` acting on the terminal object `T`, so queries are constant‑time:

> Q(v, P) = P^#(T)

## Install

```bash
pip install onestep
```

(or build from source with `python -m build` and `pip install dist/*.whl`)

## Quick Start

```python
from onestep import collapse_to_terminal, TERMINAL
from onestep.hierarchy import Node

root = Node("Root")
root.add_child(Node("Child"))
t = collapse_to_terminal(root)
assert t is TERMINAL
print(t)  # Terminal
```

## CLI

```bash
onestep --demo
```

## Why O(1)?

The *pre‑collapse* phase is a one‑time cost when data changes. Queries apply to the terminal object `T` only; they no longer depend on the size of the hierarchy.

## License

MIT © 2025 Your Name
