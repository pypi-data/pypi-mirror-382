from .hierarchy import Node
from typing import Dict, Set, Iterable
import hashlib

def ensure_collapsed(term: Node) -> None:
    if not hasattr(term, "flags") or term.flags is None:
        term.flags = {}
    # no-op collapse; here just ensures flags exists

def collapse_hash(pb: Dict[str, Set[int]]) -> str:
    h = hashlib.sha256()
    for k in sorted(pb.keys()):
        h.update(k.encode())
        for v in sorted(pb[k]):
            h.update(v.to_bytes(8, "little", signed=False))
    return h.hexdigest()
