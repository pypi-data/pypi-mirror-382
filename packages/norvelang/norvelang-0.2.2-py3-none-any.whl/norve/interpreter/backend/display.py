"""
Display and use functionality for the backend.

This module provides the complex use() method logic for displaying data with
column selection, expression evaluation, and formatting.
"""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from lark import Tree, Token
from .column_utils import extract_col_name, find_best_key
from ..expr_eval import eval_expr_node, extract_simple_var_name
from ...ast.expr import Var
from ...ast.agg import AggFunc
from ..ast_utils import find_agg_funcs
from ...api.utils import process_column_selection


def process_columns_with_display_funcs(columns, rows_to_use):
    """
    Process column selection using display backend functions.
    
    This function provides a clean interface for column processing
    using the standard display functions.
    
    Args:
        columns: List of (col_expr, alias) tuples
        rows_to_use: List of row dictionaries
        
    Returns:
        Tuple of (out_rows, col_names)
    """
    return process_column_selection(
        columns,
        rows_to_use,
        expand_wildcard_columns,
        evaluate_column_expression,
        extract_col_name,
    )


def _find_var_in_tree(node):
    """Helper function to find Var nodes in Tree structures."""
    if isinstance(node, Var):
        return node
    if isinstance(node, Tree) and hasattr(node, "children"):
        for child in node.children:
            result = _find_var_in_tree(child)
            if result:
                return result
    return None


def expand_wildcard_columns(
    columns: List[Tuple], rows_to_use: List[Dict]
) -> List[Tuple]:
    """Expand any alias.* patterns and * wildcard in column specifications."""
    expanded_columns = []
    for col_expr, alias in columns:
        # Check for * wildcard
        if isinstance(col_expr, Token) and col_expr.type == "STAR":
            # This is a * wildcard - expand it to all columns
            if rows_to_use:
                sample_row = rows_to_use[0]
                # Add each column as a separate Var
                for col in sample_row.keys():
                    expanded_columns.append((Var(name=col), None))
            # If no rows, skip this expression
            continue

        # Extract Var from Tree structure if needed
        actual_var = None
        if isinstance(col_expr, Var):
            actual_var = col_expr
        else:
            # Check if this is a Tree containing a Var
            if isinstance(col_expr, Tree):
                actual_var = _find_var_in_tree(col_expr)

        if actual_var and actual_var.name.endswith(".*"):
            # This is an alias.* pattern - expand it to all columns with that prefix
            alias_prefix = actual_var.name[:-1]  # Remove the '*' to get "alias."
            if rows_to_use:
                # Get all column names that start with this alias prefix
                sample_row = rows_to_use[0]
                matching_cols = [
                    col for col in sample_row.keys() if col.startswith(alias_prefix)
                ]
                # Add each matching column as a separate Var
                for col in matching_cols:
                    expanded_columns.append((Var(name=col), None))
            # If no matching columns found, skip this expression
        else:
            # Regular column expression
            expanded_columns.append((col_expr, alias))

    return expanded_columns


def _determine_column_name(col_expr, alias: Optional[str]) -> str:
    """Determine the column name from expression and alias."""
    if alias is not None and alias != "None":
        return str(alias)

    col_name = extract_col_name(col_expr)
    if not col_name or col_name == "None":
        col_name = str(col_expr)
    return str(col_name)


def _get_aggregation_key(agg_func) -> str:
    """Extract aggregation key from AggFunc."""
    if hasattr(agg_func.arg, "name"):
        arg_str = agg_func.arg.name
    elif hasattr(agg_func.arg, "raw"):
        arg_str = agg_func.arg.raw
    else:
        # For complex args (like Tree nodes), try to extract variable name
        arg_str = extract_simple_var_name(agg_func.arg)
    return f"{agg_func.name}({arg_str})"


def _evaluate_aggregation_expression(col_expr, row) -> Any:
    """Evaluate aggregation expressions."""

    # Check if this expression contains an AggFunc (possibly nested in a Tree)
    agg_func = None
    if isinstance(col_expr, AggFunc):
        agg_func = col_expr
    else:
        # Look for AggFunc nested in Tree structures
        agg_funcs = find_agg_funcs(col_expr)
        if agg_funcs:
            agg_func = agg_funcs[0]  # Use the first one found

    if agg_func is not None:
        agg_key = _get_aggregation_key(agg_func)
        # Only try aggregation lookup if the key exists in the row
        if agg_key in row:
            return row.get(agg_key)
        # Not an aggregation result, evaluate as a regular expression
        return eval_expr_node(col_expr, row)

    return None


def _evaluate_variable_expression(col_expr, row, row_keys) -> Any:
    """Evaluate variable expressions."""
    if isinstance(col_expr, Var):
        req = extract_col_name(col_expr)
        key = req
        if key not in row_keys:
            key = find_best_key(req, row_keys)
        return row.get(key, None)

    return None


def _evaluate_string_expression(col_expr, row) -> Any:
    """Evaluate string expressions with potential nested access."""
    if isinstance(col_expr, str):
        if col_expr in row:
            return row[col_expr]
        if "." in col_expr:
            parts = col_expr.split(".")
            v = row
            for p in parts:
                if isinstance(v, dict) and p in v:
                    v = v[p]
                else:
                    v = None
                    break
            return v
    return None


def evaluate_column_expression(
    col_expr, alias: Optional[str], row: Dict, row_keys: List[str]
) -> Tuple[str, Any]:
    """Evaluate a column expression and return the column name and value."""
    # Determine column name
    col_name = _determine_column_name(col_expr, alias)

    # Try different evaluation strategies
    # 1. Check for aggregation expressions
    val = _evaluate_aggregation_expression(col_expr, row)
    if val is not None:
        return col_name, val

    # 2. Check for variable expressions
    val = _evaluate_variable_expression(col_expr, row, row_keys)
    if val is not None:
        return col_name, val

    # 3. Check for string expressions
    val = _evaluate_string_expression(col_expr, row)
    if val is not None:
        return col_name, val

    # 4. Default: try to evaluate as general expression
    try:
        val = eval_expr_node(col_expr, row)
    except (KeyError, AttributeError, TypeError):
        # Fallback to None if expression evaluation fails
        val = None

    return col_name, val


def use_data(
    rows: List[Dict],
    columns: Optional[List[Tuple]] = None,
    limit: Optional[int] = None,
    default_limit: Optional[int] = None,
) -> None:
    """Display data with optional column selection and limit."""
    # Apply limit
    n = limit if limit is not None else default_limit
    if n is None:
        n = len(rows) if rows else 0
    rows_to_use = rows[:n]

    if columns is not None:
        # Use shared column processing utility
        out_rows, col_names = process_columns_with_display_funcs(
            columns,
            rows_to_use,
        )

        rows_to_use = out_rows

        # Remove duplicates from column names while preserving order
        seen = set()
        col_names_unique = []
        for c in col_names:
            if c not in seen:
                col_names_unique.append(c)
                seen.add(c)

    # Display the results
    if not rows_to_use or (isinstance(rows_to_use, list) and len(rows_to_use) == 0):
        print("No rows to display")
    else:
        fixed_rows = list(rows_to_use)
        if columns is not None:
            df = pd.DataFrame.from_records(fixed_rows, columns=col_names_unique)
        else:
            df = pd.DataFrame.from_records(fixed_rows)

        # Print the DataFrame with dimensions
        rows, cols = df.shape
        print(f"=== {rows} x {cols} ===\n")
        print(df)
