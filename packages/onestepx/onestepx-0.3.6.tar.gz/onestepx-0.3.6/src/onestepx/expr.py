import re
from typing import Dict, Set

TOKEN = re.compile(r'(\s+|[&|()~\-])')

def compile_expr(expr: str):
    def _tokens(e: str):
        for t in TOKEN.split(e):
            if t and t.strip() != "":
                yield t
    tokens = list(_tokens(expr))
    code = " ".join([f"m['{t}']" if t not in "&|()~-()" else t for t in tokens])
    # operators map to Python set ops via wrapper dict m
    def _eval(m: Dict[str, Set[int]]) -> Set[int]:
        return eval(code, {"m": m})
    return _eval
