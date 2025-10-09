"""
Column resolution utilities for the backend.

This module provides optimized column resolution, key finding, and column mapping utilities.
"""

from typing import List, Optional
from lark import Tree, Token
from ...ast.expr import BinaryOp, Var
from ...ast.agg import AggFunc


def resolve_column_fast(columns: List[str], key: str) -> str:
    """Optimized column resolution using early returns and cached lookups."""
    # Support $table.column syntax - remove $ prefix
    if key.startswith("$") and "." in key:
        key = key[1:]

    # Fast path: exact match first
    if key in columns:
        return key

    # Handle qualified names (table.column)
    if "." in key:
        result = _handle_qualified_name(key, columns)
        if result:
            return result

    # Use lowercase mapping for case-insensitive match
    result = _find_case_insensitive_match(key, columns)
    if result:
        return result

    # Partial match - find first column containing the key
    result = _find_partial_match(key, columns)
    if result:
        return result

    # No match found - return the key as-is
    return key


def _handle_qualified_name(key: str, columns: List[str]) -> Optional[str]:
    """Handle qualified table.column names."""
    _, col_part = key.split(".", 1)

    # Try exact qualified match first
    if key in columns:
        return key

    # Try just the column part
    if col_part in columns:
        return col_part

    # Try case-insensitive match for column part
    col_lower = col_part.lower()
    for col in columns:
        if col.lower() == col_lower:
            return col
    return None


def _find_case_insensitive_match(key: str, columns: List[str]) -> Optional[str]:
    """Find case-insensitive match."""
    key_lower = key.lower()
    lower_map = {col.lower(): col for col in columns}
    return lower_map.get(key_lower)


def _find_partial_match(key: str, columns: List[str]) -> Optional[str]:
    """Find partial match - first column containing the key."""
    for col in columns:
        if key in col:
            return col
    return None


def _normalize_requested_key(requested: str) -> str:
    """Normalize the requested key by removing $ prefix if present."""
    if requested.startswith("$") and "." in requested:
        return requested[1:]
    return requested


def _find_exact_match(requested: str, row_keys: List[str]) -> Optional[str]:
    """Find exact match for the requested key."""
    if requested in row_keys:
        return requested
    return None


def _find_dotted_key_match(requested: str, row_keys: List[str]) -> Optional[str]:
    """Find best match for dotted keys (table.column format)."""
    if "." not in requested:
        return None

    # Try exact match first
    for k in row_keys:
        if k == requested:
            return k

    req_prefix, req_col = requested.split(".", 1)

    # Try various matching strategies
    result = _try_dotted_key_strategies(req_prefix, req_col, row_keys)
    return result


def _try_dotted_key_strategies(
    req_prefix: str, req_col: str, row_keys: List[str]
) -> Optional[str]:
    """Try different strategies for matching dotted keys."""
    # Strategy 1: match keys that end with the requested column and have a similar prefix
    matches = [
        k
        for k in row_keys
        if k.endswith(f".{req_col}") and k.split(".", 1)[0].startswith(req_prefix)
    ]
    if len(matches) == 1:
        return matches[0]

    # Strategy 2: any key that ends with the column name
    matches = [k for k in row_keys if k.endswith(f".{req_col}")]
    if len(matches) == 1:
        return matches[0]

    # Strategy 3: try base column name
    if req_col in row_keys:
        return req_col

    # Strategy 4: case-insensitive match for base column
    matches = [k for k in row_keys if k.lower() == req_col.lower()]
    if len(matches) == 1:
        return matches[0]

    return None


def _find_simple_key_match(requested: str, row_keys: List[str]) -> Optional[str]:
    """Find match for simple (non-dotted) keys."""
    # Exact match
    matches = [k for k in row_keys if k == requested]
    if len(matches) == 1:
        return matches[0]

    # Case-insensitive match
    matches = [k for k in row_keys if k.lower() == requested.lower()]
    if len(matches) == 1:
        return matches[0]

    # Find keys containing the requested string
    matches = [k for k in row_keys if requested in k]
    if len(matches) == 1:
        return matches[0]

    return None


def find_best_key(requested: str, row_keys: List[str]) -> str:
    """Find the best matching key for a requested column name."""
    requested = _normalize_requested_key(requested)

    # Try exact match first
    exact_match = _find_exact_match(requested, row_keys)
    if exact_match:
        return exact_match

    # Try dotted key matching
    dotted_match = _find_dotted_key_match(requested, row_keys)
    if dotted_match:
        return dotted_match

    # Try simple key matching for non-dotted requests
    if "." not in requested:
        simple_match = _find_simple_key_match(requested, row_keys)
        if simple_match:
            return simple_match

    # Try additional fallback patterns
    result = _try_fallback_patterns(requested, row_keys)
    if result:
        return result

    # Final fallback: return first available key or the requested key
    return row_keys[0] if row_keys else requested


def _try_fallback_patterns(requested: str, row_keys: List[str]) -> Optional[str]:
    """Try additional fallback matching patterns."""
    # Pattern 1: keys ending with requested name
    matches = [k for k in row_keys if k.endswith(f".{requested}")]
    if len(matches) == 1:
        return matches[0]

    # Pattern 2: case-insensitive exact match
    matches = [k for k in row_keys if k.lower() == requested.lower()]
    if len(matches) == 1:
        return matches[0]

    # Pattern 3: keys containing the requested string
    matches = [k for k in row_keys if requested in k]
    if len(matches) == 1:
        return matches[0]

    # Pattern 4: case-insensitive fallback (first match)
    for k in row_keys:
        if k.lower() == requested.lower():
            return k

    # Pattern 5: return first match from previous search
    if matches:
        return matches[0]

    return None


def _reconstruct_expression(node):
    """Reconstruct a readable expression string from AST nodes"""
    # Handle simple node types
    if hasattr(node, "name"):  # Var
        return node.name
    if hasattr(node, "value"):  # Literal
        return str(node.value)

    # Handle BinaryOp
    if hasattr(node, "op"):
        left_str = _reconstruct_expression(node.left)
        right_str = _reconstruct_expression(node.right)
        return f"({left_str} {node.op} {right_str})"

    # Handle Tree nodes
    if isinstance(node, Tree):
        result = _handle_tree_node_reconstruction(node)
        if result:
            return result

    # Default fallback
    return str(node)


def _handle_tree_node_reconstruction(node):
    """Handle Tree node reconstruction for expressions."""
    if node.data in ["prod_expr", "sum_expr", "power_expr"] and len(node.children) == 1:
        return _reconstruct_expression(node.children[0])
    return None


def _handle_tree_expression(expr, token_cls, binary_op_cls):
    """Handle Tree-based expressions for column name extraction."""
    if not hasattr(expr, "data"):
        return "expr"

    # Check if this is a simple identifier wrapped in expression trees
    if expr.data == "sum_expr" and len(expr.children) == 1:
        result = _handle_sum_expr_child(expr.children[0], binary_op_cls)
        if result:
            return result

    if expr.data == "ident" and len(expr.children) == 1:
        result = _handle_ident_child(expr.children[0], token_cls)
        if result:
            return result

    # Handle mathematical expressions
    if expr.data in ["sum_expr", "mul_expr", "add_expr", "sub_expr", "pow_expr"]:
        return f"expr_{expr.data}"

    return f"expr_{expr.data}"


def _handle_sum_expr_child(child, binary_op_cls):
    """Handle sum expression child nodes."""
    if (
        hasattr(child, "data")
        and child.data == "prod_expr"
        and len(child.children) == 1
    ):
        inner_child = child.children[0]
        if hasattr(inner_child, "name"):  # It's a Var object
            return inner_child.name
        if isinstance(inner_child, binary_op_cls):
            return _reconstruct_expression(inner_child)

    if isinstance(child, binary_op_cls):
        return _reconstruct_expression(child)

    return None


def _handle_ident_child(child, token_cls):
    """Handle identifier child nodes."""
    if isinstance(child, token_cls):
        return str(child.value)
    return str(child)


def _handle_agg_func_name(expr):
    """Handle aggregation function name extraction."""
    arg = expr.arg
    if hasattr(arg, "name"):
        arg_str = arg.name
    elif hasattr(arg, "raw"):
        arg_str = arg.raw
    else:
        arg_str = str(arg)
    return f"{expr.name}({arg_str})"


def extract_col_name(expr) -> str:
    """Extract a readable column name from an expression."""
    # Simple string case
    if isinstance(expr, str):
        return expr

    # Handle specific object types
    result = _handle_specific_expr_types(expr)
    if result is not None:
        return result

    # Handle Tree objects
    if isinstance(expr, Tree):
        return _handle_tree_expression(expr, Token, BinaryOp)

    # Handle dotted identifier
    if hasattr(expr, "data") and expr.data == "dotted_ident":
        return ".".join(str(child) for child in expr.children)

    # Fallback
    return str(expr)


def _handle_specific_expr_types(expr) -> Optional[str]:
    """Handle specific expression types and return column name if applicable."""
    # Handle BinaryOp directly (when not wrapped in a Tree)
    if isinstance(expr, BinaryOp):
        return _reconstruct_expression(expr)

    # Handle Var objects
    if isinstance(expr, Var):
        return expr.name

    # Handle AggFunc objects
    if isinstance(expr, AggFunc):
        return _handle_agg_func_name(expr)

    return None


def get_join_var_fast(right_alias: Optional[str], right_source: Optional[str]) -> str:
    """Fast join variable determination using optimized logic."""
    if right_alias:
        return right_alias

    if isinstance(right_source, str) and right_source.startswith("$"):
        return right_source[1:]
    if isinstance(right_source, str):
        # Use file/let variable name as prefix
        return (
            right_source.split("/")[-1].split(".")[0]
            if "/" in right_source
            else right_source.split(".")[0]
        )
    return "right"
