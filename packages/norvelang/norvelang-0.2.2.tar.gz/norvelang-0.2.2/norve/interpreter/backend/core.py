"""
Core backend implementation for executing norvelang pipeline operations.

This module provides the main ListBackend class with optimized operations
and imports from the specialized modules.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import csv
import pandas as pd

from .column_utils import resolve_column_fast, find_best_key, get_join_var_fast
from .joins import perform_join, JoinConfig, JoinKeys, JoinAliases
from .display import use_data
from .grouping import perform_grouping
from ..expr_eval import eval_expr_node


@dataclass
class JoinParams:
    """Parameters for join operations."""
    join_type: str
    other_rows: List[Dict[str, Any]]
    left_key: Optional[str]
    right_key: Optional[str]
    left_alias: Optional[str] = None
    right_alias: Optional[str] = None
    right_source: Optional[str] = None


# Performance constants
_SMALL_DATASET_THRESHOLD = 100  # Threshold for algorithm selection
_CACHE_THRESHOLD = 500  # Threshold for caching DataFrames


class ListBackend:
    """Optimized backend that operates on lists of dictionaries using pandas for complex operations.

    This backend is optimized for performance with:
    - Fast column resolution using early returns and cached lookups
    - Memory-efficient data handling with minimal copying
    - Optimized join operations using set operations and dict comprehensions
    - Efficient grouping with cached field resolution
    """

    _show_counter: int = 0

    def __init__(self, rows: Union[List[Dict], pd.DataFrame]) -> None:
        """Initialize backend with data rows.

        Args:
            rows: List of dictionaries or pandas DataFrame containing the data
        """
        if isinstance(rows, pd.DataFrame):
            # Handle fillna compatibility with newer pandas versions
            try:
                df = rows.fillna(value=None)
            except ValueError:
                # For newer pandas versions, use different approach
                df = rows.where(pd.notnull(rows), None)
            self.rows = df.to_dict(orient="records")
        elif isinstance(rows, list):
            # Direct assignment for lists - avoid DataFrame conversion if not needed
            self.rows = rows if rows else []
        else:
            self.rows = []
        self._last_group_by_fields: Optional[List[str]] = None

        # Performance optimization: pre-compute if we should use caching strategies
        self._use_caching = len(self.rows) > _CACHE_THRESHOLD if self.rows else False

    def _should_use_pandas_optimizations(self) -> bool:
        """Determine if pandas optimizations should be used based on data size."""
        return len(self.rows) > _SMALL_DATASET_THRESHOLD

    def _get_columns_fast(self) -> List[str]:
        """Fast column extraction using set operations for large datasets."""
        if not self.rows:
            return []
        # For small datasets, use simple approach
        if len(self.rows) <= _SMALL_DATASET_THRESHOLD:
            return list(self.rows[0].keys()) if self.rows else []
        # For large datasets, collect all unique keys
        all_keys = set()
        for row in self.rows:
            all_keys.update(row.keys())
        return list(all_keys)

    def order(self, orderings: List[Tuple[str, str]]) -> "ListBackend":
        """Sort the data by specified columns and directions.

        Args:
            orderings: List of (column, direction) tuples where direction is 'asc' or 'desc'

        Returns:
            Self for method chaining
        """
        if not self.rows:
            return self

        # Use pandas for efficient sorting on larger datasets
        if self._should_use_pandas_optimizations():
            df = pd.DataFrame(self.rows)
            sort_columns = []
            ascending = []

            for col, direction in orderings:
                resolved_col = resolve_column_fast(list(df.columns), col)
                sort_columns.append(resolved_col)
                ascending.append(direction.lower() == "asc")

            df_sorted = df.sort_values(by=sort_columns, ascending=ascending)
            self.rows = df_sorted.to_dict(orient="records")
        else:
            # Use native Python sorting for smaller datasets
            for col, direction in reversed(
                orderings
            ):  # Reverse for stable multi-key sort
                resolved_col = resolve_column_fast(self._get_columns_fast(), col)
                reverse = direction.lower() == "desc"

                # Handle None values by treating them as lower than any other value
                self.rows.sort(
                    key=lambda r, col=resolved_col: (
                        (0, 0) if r.get(col) is None else (1, r.get(col))
                    ),
                    reverse=reverse,
                )

        return self

    def limit(self, n: Optional[int]) -> "ListBackend":
        """Limit the number of rows.

        Args:
            n: Maximum number of rows to keep, or None for no limit

        Returns:
            Self for method chaining
        """
        if n is not None and n >= 0:
            self.rows = self.rows[:n]
        return self

    def join(self, join_params: JoinParams) -> "ListBackend":
        """Perform a join operation with another dataset.

        Args:
            join_params: JoinParams object containing join configuration

        Returns:
            New ListBackend with joined data
        """
        # Create DataFrames
        left_df = pd.DataFrame(self.rows)
        right_df = pd.DataFrame(join_params.other_rows)

        # Create JoinConfig and perform join
        keys = JoinKeys(
            left_key=join_params.left_key,
            right_key=join_params.right_key
        )
        aliases = JoinAliases(
            left_alias=join_params.left_alias,
            right_alias=join_params.right_alias,
            right_source=join_params.right_source
        )
        config = JoinConfig(
            left_df=left_df,
            right_df=right_df,
            join_type=join_params.join_type,
            keys=keys,
            aliases=aliases
        )

        result_df = perform_join(config)
        return ListBackend(result_df.to_dict(orient="records"))

    def use(self, columns=None, limit=None):
        """Display the data with optional column selection and limit."""
        use_data(self.rows, columns, limit, getattr(self, "_default_limit", None))
        return self

    def group(self, by_fields, aggs):
        """Group the data by specified fields and apply aggregations."""
        self.rows = perform_grouping(self.rows, by_fields, aggs)
        self._last_group_by_fields = list(by_fields) if by_fields else None
        return self

    def save(self, path):
        """Save the data to a CSV file."""
        path = Path(path)
        if not self.rows:
            path.write_text("", encoding="utf-8")
            return self

        # Collect all unique keys from all rows
        all_keys = set()
        for row in self.rows:
            all_keys.update(row.keys())
        keys = list(all_keys)

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in self.rows:
                # Fill missing keys with empty string
                row_out = {k: ("" if r.get(k) is None else r.get(k)) for k in keys}
                writer.writerow(row_out)
        return self

    def filter(self, condition):
        """Filter rows based on a condition."""
        filtered_rows = []
        for r in self.rows:
            if eval_expr_node(condition, r):
                filtered_rows.append(r)
        self.rows = filtered_rows
        return self

    # Deprecated methods for backward compatibility
    def _resolve_column_fast(self, columns: List[str], key: str) -> str:
        """Deprecated: use column_utils.resolve_column_fast instead."""
        return resolve_column_fast(columns, key)

    def _get_join_var_fast(
        self, right_alias: Optional[str], right_source: Optional[str]
    ) -> str:
        """Deprecated: use column_utils.get_join_var_fast instead."""
        return get_join_var_fast(right_alias, right_source)

    def _find_best_key(self, requested: str, row_keys: List[str]) -> str:
        """Deprecated: use column_utils.find_best_key instead."""
        return find_best_key(requested, row_keys)
