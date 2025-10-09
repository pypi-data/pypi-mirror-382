"""
Group operations for the backend.

This module provides optimized grouping operations with aggregation functions.
"""

import math
from typing import List, Dict, Any
from .column_utils import find_best_key
from ..expr_eval import eval_expr_node, extract_simple_var_name


def _resolve_grouping_fields(
    by_fields: List[str], first_row_keys: List[str]
) -> List[str]:
    """Resolve and cache grouping fields."""
    return [find_best_key(f, first_row_keys) for f in by_fields]


def _create_group_buckets(
    rows: List[Dict], by_fields: List[str], first_row_keys: List[str]
) -> dict:
    """Create buckets for grouping rows by key fields."""
    buckets = {}
    resolved_fields_cache = _resolve_grouping_fields(by_fields, first_row_keys)

    for r in rows:
        key = tuple(r.get(f, None) for f in resolved_fields_cache)
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(r)

    return buckets


def _propagate_constant_columns(
    out: Dict, group_rows: List[Dict], first_row_keys: List[str]
):
    """Propagate constant columns that have the same value across all rows in group."""
    if not group_rows:
        return

    for col in first_row_keys:
        if col in out:
            continue
        val0 = group_rows[0].get(col, None)
        # Use all() with generator for memory efficiency
        if all(r.get(col, None) == val0 for r in group_rows):
            out[col] = val0


def _get_agg_arg_string(agg) -> str:
    """Extract argument string from aggregation function."""
    if hasattr(agg.arg, "name"):
        return agg.arg.name
    if hasattr(agg.arg, "raw"):
        return agg.arg.raw
    # For complex args (like Tree nodes), try to extract variable name
    return extract_simple_var_name(agg.arg)


def _compute_count_aggregation(agg, group_rows: List[Dict]) -> int:
    """Compute count aggregation (count(*) or count(column))."""
    if hasattr(agg, "arg") and hasattr(agg.arg, "raw") and agg.arg.raw == "*":
        # count(*) - count all rows in the group
        return len(group_rows)
    if hasattr(agg, "arg"):
        # count(column) - count non-null values
        seq = [eval_expr_node(agg.arg, r) for r in group_rows]
        filtered_seq = [
            s
            for s in seq
            if s is not None and not (isinstance(s, float) and math.isnan(s))
        ]
        return len(filtered_seq)
    return 0


def _compute_numeric_aggregation(func: str, agg, group_rows: List[Dict]):
    """Compute numeric aggregations (sum, min, max, avg)."""
    # Other aggregation functions
    seq = [eval_expr_node(agg.arg, r) for r in group_rows]
    seq2 = []
    for s in seq:
        if s is None:
            continue
        if isinstance(s, (int, float)):
            seq2.append(float(s))
        elif isinstance(s, str):
            try:
                seq2.append(float(s))
            except ValueError:
                continue
        # skip non-numeric

    if func == "sum":
        return sum(seq2) if seq2 else None
    if func == "min":
        return min(seq2) if seq2 else None
    if func == "max":
        return max(seq2) if seq2 else None
    if func in ("avg", "mean"):
        return sum(seq2) / len(seq2) if seq2 else None
    return None


def _compute_aggregations(out: Dict, aggs: Dict[str, Any], group_rows: List[Dict]):
    """Compute all aggregations for a group."""
    for out_name, agg in aggs.items():
        # Safely handle both string and token names
        func_name = agg.name
        if hasattr(func_name, "value"):
            func_name = str(func_name.value)
        elif not isinstance(func_name, str):
            func_name = str(func_name)
        func = func_name.lower()

        # Always use the function call string as the key, e.g., avg(age)
        if hasattr(agg, "arg"):
            arg_str = _get_agg_arg_string(agg)
            agg_key = f"{agg.name}({arg_str})"
        else:
            agg_key = str(out_name)

        # Compute aggregate value
        if func == "count":
            agg_value = _compute_count_aggregation(agg, group_rows)
        else:
            agg_value = _compute_numeric_aggregation(func, agg, group_rows)

        # Store under both the function call string and the alias (out_name) if different
        out[agg_key] = agg_value
        if str(out_name) != agg_key:
            out[str(out_name)] = agg_value


def perform_grouping(
    rows: List[Dict], by_fields: List[str], aggs: Dict[str, Any]
) -> List[Dict]:
    """
    Perform grouping operation with aggregations.

    Args:
        rows: List of data rows
        by_fields: List of fields to group by
        aggs: Dictionary of aggregation functions

    Returns:
        List of grouped rows with aggregations
    """
    if not rows:
        return []

    # Pre-compute row keys once for efficiency
    first_row_keys = list(rows[0].keys()) if rows else []

    # Fast grouping using optimized key resolution
    buckets = _create_group_buckets(rows, by_fields, first_row_keys)

    result = []
    for key, group_rows in buckets.items():
        out = {str(f): key[i] for i, f in enumerate(by_fields)}

        # Propagate constant columns efficiently
        _propagate_constant_columns(out, group_rows, first_row_keys)

        # Compute all aggs for this group
        _compute_aggregations(out, aggs, group_rows)

        result.append(out)

    return result
