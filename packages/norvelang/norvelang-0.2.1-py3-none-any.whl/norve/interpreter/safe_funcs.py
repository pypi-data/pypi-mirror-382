"""Safe functions available in Norvelang expressions."""

import datetime
import math
import pandas as pd

from ..token_utils import normalize_token


def _normalize_value(val):
    """Convert tokens to their values."""
    return normalize_token(val)


SAFE_FUNCS = {
    "len": lambda s: (
        len(_normalize_value(s)) if hasattr(_normalize_value(s), "__len__") else 0
    ),
    "int": lambda x: int(_normalize_value(x)),
    "float": lambda x: float(_normalize_value(x)),
    "str": lambda x: str(_normalize_value(x)),
    "upper": lambda s: (
        _normalize_value(s).upper()
        if hasattr(_normalize_value(s), "upper")
        else str(_normalize_value(s))
    ),
    "lower": lambda s: (
        _normalize_value(s).lower()
        if hasattr(_normalize_value(s), "lower")
        else str(_normalize_value(s))
    ),
    "abs": abs,
    "round": round,
    "math": math,
    "count": len,
    "sum": sum,
    "min": min,
    "max": max,
    "avg": lambda seq: sum(seq) / len(seq) if seq else None,
    "sub": lambda s, start, length=None: (
        s[int(start) : (int(start) + int(length))]
        if length is not None
        else s[int(start) :] if isinstance(s, str) else s
    ),
    "substr": lambda s, start, length=None: (
        s[int(start) : (int(start) + int(length))]
        if length is not None
        else s[int(start) :] if isinstance(s, str) else s
    ),
    "left": lambda s, n: s[: int(n)] if isinstance(s, str) else s,
    "right": lambda s, n: s[-int(n) :] if isinstance(s, str) else s,
    "trim": lambda s: s.strip() if isinstance(s, str) else s,
    "ltrim": lambda s: s.lstrip() if isinstance(s, str) else s,
    "rtrim": lambda s: s.rstrip() if isinstance(s, str) else s,
    "contains": lambda s, substr: (
        substr in s if isinstance(s, str) and isinstance(substr, str) else False
    ),
    "startswith": lambda s, prefix: (
        s.startswith(prefix)
        if isinstance(s, str) and isinstance(prefix, str)
        else False
    ),
    "endswith": lambda s, suffix: (
        s.endswith(suffix) if isinstance(s, str) and isinstance(suffix, str) else False
    ),
    "replace": lambda s, old, new: s.replace(old, new) if isinstance(s, str) else s,
    "year": lambda d: (
        datetime.datetime.strptime(d, "%Y-%m-%d").year
        if isinstance(d, str) and "-" in d
        else None
    ),
    "now": lambda: datetime.datetime.now().isoformat(),
    "curdate": lambda: datetime.date.today().isoformat(),
    "isnull": pd.isna,
    "notnull": pd.notna,
}
