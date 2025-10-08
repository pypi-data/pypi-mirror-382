"""Simple ordinal display helper (toy model)."""
from __future__ import annotations
from typing import List, Tuple

class Ordinal:
    def __init__(self, coeffs: List[Tuple[int, int]]):
        self.coeffs = coeffs

    def __repr__(self) -> str:
        if not self.coeffs:
            return "0"
        terms = []
        for coeff, exp in self.coeffs:
            if exp == 0:
                terms.append(f"{coeff}")
            elif coeff == 1:
                terms.append(f"ω^{exp}")
            else:
                terms.append(f"{coeff}·ω^{exp}")
        return " + ".join(terms)
