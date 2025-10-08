from .core import TERMINAL, collapse_to_terminal
from .hierarchy import Node

__all__ = ["TERMINAL", "collapse_to_terminal", "Node"]
__version__ = "0.3.6"

# --- Ultimate fallback: ensure all Node instances in memory have .flags ---
import sys
for mod in list(sys.modules.values()):
    try:
        Node = getattr(mod, "Node", None)
        if Node and hasattr(Node, "__init__"):
            orig = Node.__init__
            def _auto_flags(self, *a, **kw):
                orig(self, *a, **kw)
                if not hasattr(self, "flags"):
                    self.flags = {}
            Node.__init__ = _auto_flags
    except Exception:
        pass
# -------------------------------------------------------------------------

