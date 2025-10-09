"""Pipeline execution engine for Norvelang."""

import json
import sqlite3
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..ast import From
from ..ast.steps import Title
from .ast_utils import find_agg_funcs
from .backend import ListBackend
from .backend.core import JoinParams
from .utils import extract_arg_value

FILE_FORMATS = {
    "csv": "csv",
    "xlsx": "excel",
    "xls": "excel",
    "sqlite": "sqlite",
    "db": "sqlite",
    "json": "json",
    "xml": "xml",
}


def _get_ext(src):
    """Return lower-case file extension without dot; defaults to empty string."""
    try:
        return Path(str(src)).suffix.lower().lstrip(".")
    except (OSError, TypeError, ValueError):
        return ""


def get_file_format(src):
    """Fast file format detection using pre-computed lookup."""
    ext = _get_ext(src)
    return FILE_FORMATS.get(ext, "csv")  # Default to CSV


def parse_json_file(src):
    """Parse JSON file into list of dicts with fast common-case handling."""
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Quick heuristic: find the first value that is a non-empty list of dicts
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return value
        return [data]

    return []


def parse_xml_file(src, extra=None):
    """
    Parse XML into list of dicts.

    Tries extra['element'] then most frequent child tag then direct children.
    """
    tree = ET.parse(src)
    root = tree.getroot()

    # If user provided specific element name, use it first
    if extra and extra.get("element"):
        el = extra["element"]
        rows = root.findall(f".//{el}") or [e for e in root if e.tag == el]
        return [{child.tag: child.text for child in r} for r in rows]

    # Count tags (skip the root tag itself)
    counter = Counter()
    for el in root.iter():
        if el is root:
            continue
        counter[el.tag] += 1

    rows = None
    if counter:
        main = counter.most_common(1)[0][0]
        if counter[main] > 1:
            rows = root.findall(f".//{main}")

    if not rows:
        rows = list(root)

    return [{child.tag: child.text for child in r} for r in rows]


def extract_simple_arg_str(arg):
    """Extract a simple variable-like string from a variety of node types."""
    if hasattr(arg, "name"):
        return arg.name

    # Use shared argument extraction utility
    return extract_arg_value(arg)


def _normalize_src_value(src_token):
    """Return a string path/identifier from various token shapes."""
    if hasattr(src_token, "value"):
        return str(src_token.value)
    return str(src_token)


def _load_rows_from_source(src_token, extra, let_tables):
    """
    Load rows from a source token or let_tables.

    Returns list[dict] or raises RuntimeError for missing info.
    """
    src = _normalize_src_value(src_token)

    # Variable lookup
    if src in let_tables:
        return let_tables[src]
    if src.startswith("$"):
        varname = src[1:]
        if varname in let_tables:
            return let_tables[varname]
        raise RuntimeError(f"Unknown variable: {src}")

    # File-based loading
    fmt = get_file_format(src)

    if fmt == "csv":
        rows = pd.read_csv(src).to_dict(orient="records")
    elif fmt == "excel":
        sheet = extra.get("sheet", 0) if extra else 0
        rows = pd.read_excel(src, sheet_name=sheet).to_dict(orient="records")
    elif fmt == "sqlite":
        table = extra.get("table") if extra else None
        if not table:
            raise RuntimeError("No table specified for SQLite source")
        with sqlite3.connect(src) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table}")
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    elif fmt == "json":
        rows = parse_json_file(src)
    elif fmt == "xml":
        rows = parse_xml_file(src, extra)
    else:
        # default to CSV
        rows = pd.read_csv(src).to_dict(orient="records")

    return rows


def _patch_group_use_aggregations(tail):
    """Pre-process Group -> Use patching to add missing aggregations."""
    for j, current_step in enumerate(tail[:-1]):
        if hasattr(current_step, "by") and hasattr(current_step, "aggs"):
            use_step = _find_next_use_step(tail, j)
            if use_step:
                _add_missing_aggregations(current_step, use_step)


def _find_next_use_step(tail, start_index):
    """Find the next Use step after a Group step, skipping Having steps."""
    for candidate in tail[start_index + 1 :]:
        tname = type(candidate).__name__
        if tname == "Use":
            return candidate
        if tname != "Having":
            break
    return None


def _add_missing_aggregations(group_step, use_step):
    """Add missing aggregations from Use step to Group step."""
    if not getattr(use_step, "columns", None):
        return

    use_aggs = {}
    for expr, _ in use_step.columns:
        for agg in find_agg_funcs(expr):
            arg_str = _extract_agg_arg_string(agg)
            key = f"{agg.name}({arg_str})"
            use_aggs[key] = agg

    # Add any missing aggregations
    for k, v in use_aggs.items():
        if k not in group_step.aggs:
            group_step.aggs[k] = v


def _extract_agg_arg_string(agg):
    """Extract argument string from aggregation function."""
    if hasattr(agg.arg, "name"):
        return agg.arg.name
    if hasattr(agg.arg, "raw"):
        return agg.arg.raw
    if hasattr(agg.arg, "value"):
        return str(agg.arg.value)
    return extract_simple_arg_str(agg.arg)


def _handle_group_step(backend, step, tail, i):
    """Handle Group step with optional Having."""
    backend.group(step.by, step.aggs)
    # immediate Having if present
    if i + 1 < len(tail) and type(tail[i + 1]).__name__ == "Having":
        backend.filter(tail[i + 1].condition)
        return i + 2  # Skip both Group and Having
    return i + 1


def _handle_join_step(backend, step, let_tables, current_alias):
    """Handle Join step and return new backend and alias."""
    src = step.source
    other_rows = None
    # Try to resolve from let_tables first
    if isinstance(src, str) and src in let_tables:
        other_rows = let_tables[src]
    else:
        other_rows = _load_rows_from_source(
            src, getattr(step, "extra", None) or {}, let_tables
        )

    if getattr(step, "alias", None):
        let_tables[step.alias] = other_rows

    join_params = JoinParams(
        join_type=step.join_type,
        other_rows=other_rows,
        left_key=step.left_key,
        right_key=step.right_key,
        left_alias=current_alias,
        right_alias=getattr(step, "alias", None),
        right_source=getattr(step, "source", None),
    )
    new_backend = backend.join(join_params)
    new_alias = getattr(step, "alias", current_alias)
    return new_backend, new_alias


def _handle_regular_step(backend, step, has_explicit_limit, explicit_limit_value):
    """Handle regular pipeline steps (Use, Filter, Map, Save, Order, Limit)."""
    tname = type(step).__name__

    if tname == "Use":
        backend.use(
            getattr(step, "columns", None),
            limit=(
                explicit_limit_value
                if has_explicit_limit
                else _get_backend_default_limit(backend)
            ),
        )
    elif hasattr(step, "condition"):
        backend.filter(step.condition)
    elif hasattr(step, "mappings"):
        backend.map(step.mappings)
    elif hasattr(step, "target"):
        backend.save(step.target)
    elif tname == "Order":
        backend.order(step.orderings)
    elif tname == "Limit":
        backend.limit(getattr(step, "n", _get_backend_default_limit(backend)))
    else:
        raise RuntimeError(f"Unsupported step: {step}")


def _compute_limit_info(tail, default_limit):
    """Compute whether an explicit Limit exists and its value."""
    has_explicit_limit = False
    explicit_limit_value = None
    for s in tail:
        if type(s).__name__ == "Limit":
            has_explicit_limit = True
            explicit_limit_value = getattr(s, "n", default_limit)
            break
    return has_explicit_limit, explicit_limit_value


def _get_backend_default_limit(backend):
    """Get the default limit from backend, handling protected access."""
    if hasattr(backend, "get_default_limit"):
        return backend.get_default_limit()
    return getattr(backend, "_default_limit", None)


def _set_backend_default_limit(backend, limit):
    """Set the default limit on backend, handling protected access."""
    if hasattr(backend, "set_default_limit"):
        backend.set_default_limit(limit)
    else:
        setattr(backend, "_default_limit", limit)


def execute_pipeline(ast, let_tables=None, default_limit=None, silent=False):
    """Top-level pipeline execution entry point (optimized)."""
    if let_tables is None:
        let_tables = {}

    # Initialize pipeline components
    backend, current_alias = _initialize_pipeline(ast, let_tables, default_limit)

    # Get flattened tail steps
    tail = _get_flattened_tail_steps(ast.steps)

    # Compute limit information
    has_explicit_limit, explicit_limit_value = _compute_limit_info(tail, default_limit)

    # Pre-process Group -> Use patching
    _patch_group_use_aggregations(tail)

    # Process pipeline steps
    config = _PipelineConfig(
        let_tables, current_alias, has_explicit_limit, explicit_limit_value
    )
    backend = _process_pipeline_steps(backend, tail, config)

    # Apply final processing
    return _finalize_pipeline(backend, tail, has_explicit_limit, explicit_limit_value, silent)


def _initialize_pipeline(ast, let_tables, default_limit):
    """Initialize the pipeline with From step and return backend and alias."""
    steps = ast.steps

    # Filter out leading Title steps and ensure pipeline starts with From
    nonmeta = [s for s in steps if not isinstance(s, Title)]
    if not nonmeta or not isinstance(nonmeta[0], From):
        raise RuntimeError("Pipeline must start with a From step")

    # Get the first From step
    start_index = steps.index(nonmeta[0])
    from_step = steps[start_index]
    extra = getattr(from_step, "extra", None) or {}

    # Load initial rows
    rows = _load_rows_from_source(from_step.source, extra, let_tables)

    # Handle alias prefixing
    alias = getattr(from_step, "alias", None)
    if alias:
        df = pd.DataFrame(rows)
        df = df.add_prefix(f"{alias}.")
        rows = df.to_dict(orient="records")
        let_tables[alias] = rows

    backend = ListBackend(rows)
    _set_backend_default_limit(backend, default_limit)

    return backend, alias


def _get_flattened_tail_steps(steps):
    """Get flattened tail steps after the From step."""
    # Filter to get non-meta steps
    nonmeta = [s for s in steps if not isinstance(s, Title)]
    start_index = steps.index(nonmeta[0])
    steps = steps[start_index:]

    # Helper to flatten nested step lists/tuples
    def flatten(steps_iterable):
        for s in steps_iterable:
            if isinstance(s, (list, tuple)):
                yield from flatten(s)
            else:
                yield s

    return list(flatten(steps[1:]))


@dataclass
class _PipelineConfig:
    """Configuration object to reduce argument passing."""

    let_tables: dict
    current_alias: str
    has_explicit_limit: bool
    explicit_limit_value: int


def _process_pipeline_steps(backend, tail, config):
    """Process all pipeline steps."""
    i = 0
    while i < len(tail):
        step = tail[i]

        # Skip Title steps
        if isinstance(step, Title):
            i += 1
            continue

        # Group step
        if hasattr(step, "by") and hasattr(step, "aggs"):
            i = _handle_group_step(backend, step, tail, i)
            continue

        # Join step
        if hasattr(step, "join_type"):
            backend, config.current_alias = _handle_join_step(
                backend, step, config.let_tables, config.current_alias
            )
            i += 1
            continue

        # Regular steps
        _handle_regular_step(
            backend, step, config.has_explicit_limit, config.explicit_limit_value
        )
        i += 1

    return backend


def _finalize_pipeline(backend, tail, has_explicit_limit, explicit_limit_value, silent=False):
    """Apply final processing and return results."""
    has_use_step = any(type(step).__name__ == "Use" for step in tail)
    if not has_explicit_limit:
        backend.limit(_get_backend_default_limit(backend))

    # If no explicit Use step, add an implicit use to display results
    # But only if not in silent mode (e.g., for let statements)
    if not has_use_step and not silent:
        backend.use(
            columns=None,
            limit=(
                explicit_limit_value
                if has_explicit_limit
                else _get_backend_default_limit(backend)
            ),
        )

    return backend.rows if backend else None
