from typing import Dict, Iterable, Set
from statistics import median

def between(start_ts: int, end_ts: int, ids: Iterable[int], last_change_ts: Dict[int,int]) -> Set[int]:
    out = set()
    get = last_change_ts.get
    for i in ids:
        ts = get(i)
        if ts is not None and start_ts <= ts < end_ts:
            out.add(i)
    return out

def sum_by(ids: Iterable[int], table: Dict[int, float]) -> float:
    get = table.get
    return float(sum(get(i, 0.0) for i in ids))

def avg_by(ids: Iterable[int], table: Dict[int, float]) -> float:
    ids = list(ids)
    if not ids: return 0.0
    return sum_by(ids, table) / len(ids)

def median_by(ids: Iterable[int], table: Dict[int, float]) -> float:
    vals = [table.get(i, 0.0) for i in ids]
    return float(median(vals)) if vals else 0.0
