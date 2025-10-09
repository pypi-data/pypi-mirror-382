"""
Statement transformers for AST transformation.

This module contains transformers for pipeline statements like where, order, join, etc.
"""

from typing import List, Any
from lark import Token
from ..token_utils import normalize_token

from ..ast import Where, Order, Limit, Join, Use, Map, Group, AggFunc, Save, Let
from ..ast.expr import Var
from ..ast.steps import Having, Title
from .utils import parse_source_with_alias


class TokenTransformers:
    """Token transformation methods."""

    def order_dir_token(self, tok):
        """Transform ORDER_DIR token."""
        return str(tok.value).lower()

    # Lark compatibility alias
    ORDER_DIR = order_dir_token

    def join_type_token(self, tok):
        """Transform JOIN_TYPE token."""
        return str(tok.value)

    # Lark compatibility alias
    JOIN_TYPE = join_type_token

    def ident_token(self, tok):
        """Transform IDENT token."""
        return str(tok.value)

    # Lark compatibility alias
    IDENT = ident_token

    def as_token(self, tok):
        """Transform AS token."""
        return str(tok.value)

    # Lark compatibility alias
    AS = as_token


class HelperTransformers:
    """Helper transformation methods."""

    def _dotted_to_str(self, val):
        """Convert dotted identifier to string."""
        if hasattr(val, "children"):
            return ".".join(str(child) for child in val.children)
        return str(val)

    def dotted_ident(self, items):
        """Transform dotted identifier."""
        # items contains the parts of the dotted identifier
        result = []
        for item in items:
            if hasattr(item, "value"):
                result.append(item.value)
            else:
                result.append(str(item))
        return ".".join(result)

    def field_list(self, items):
        """Transform field list."""
        # Each item should be converted to string if it's not already
        fields = []
        for item in items:
            if hasattr(item, "name"):
                fields.append(item.name)
            else:
                fields.append(str(item))
        return fields

    def source(self, items):
        """Transform source."""
        return items[0]

    def source_with_alias(self, items):
        """Transform source with alias."""
        if len(items) == 3 and str(items[1]).lower() == "as":
            # source AS alias (3 items: source, "as", alias)
            return (items[0], items[2])
        if len(items) == 2:
            # source alias (2 items: source, alias)
            return (items[0], items[1])
        # Just source (1 item)
        return (items[0], None)


class StatementTransformers(TokenTransformers, HelperTransformers):
    """Main statement transformation methods."""

    def title_stmt(self, items: List[Any]) -> Title:
        """Transform title statement."""
        return Title(items[0])

    def having_stmt(self, items: List[Any]) -> Having:
        """Transform having statement."""
        return Having(items[0])

    def where_stmt(self, items: List[Any]) -> Where:
        """Transform where statement."""
        return Where(items[0])

    def order_stmt(self, items):
        """Transform order statement."""
        # items[0] is order_list
        orderings = []
        for item in items[0]:
            if isinstance(item, tuple):
                field, direction = item
                orderings.append((field, direction))
            else:
                # Default to ascending if no direction specified
                orderings.append((item, "asc"))
        return Order(orderings)

    def order_list(self, items):
        """Transform order list."""
        # items contains multiple order_key items
        return items

    def order_key(self, items):
        """Transform order key."""
        # items[0] is dotted_ident, items[1] might be ORDER_DIR
        field = items[0]
        direction = "asc"  # default
        if len(items) > 1 and items[1] is not None:
            direction = str(items[1]).lower()
        return (field, direction)

    def limit_stmt(self, items):
        """Transform limit statement."""
        # items[0] is a number (Literal)
        limit_val = items[0].value if hasattr(items[0], "value") else items[0]
        # Ensure it's an integer
        return Limit(int(limit_val))

    def join_stmt(self, items):
        """Transform join statement."""
        join_type = items[0] if isinstance(items[0], str) else str(items[0])
        source_info = items[1]

        # Handle source with possible alias
        source, alias = parse_source_with_alias(source_info)

        # Initialize variables
        left_key, right_key = None, None
        extra = {}

        # Check if there are join keys (for JOIN_TYPE with "on" clause)
        if len(items) > 2:
            # Look for join keys vs extra params
            for item in items[2:]:
                if item is not None:
                    if isinstance(item, tuple) and len(item) == 2:
                        # This is join keys (left_key, right_key)
                        left_key, right_key = item
                    elif isinstance(item, dict):
                        # This is extra_params
                        extra = item

        return Join(
            join_type=join_type,
            source=source,
            alias=alias,
            left_key=left_key,
            right_key=right_key,
            extra=extra,
        )

    def join_keys(self, items):
        """Transform join keys."""
        # items should be [left_key, right_key]
        if len(items) == 2:
            left_key = self._dotted_to_str(items[0])
            right_key = self._dotted_to_str(items[1])
            return (left_key, right_key)
        # Handle single key case (natural join or same key name)
        key = self._dotted_to_str(items[0])
        return (key, key)

    def use_stmt(self, items):
        """Transform use statement."""
        if len(items) == 0:
            # use with no arguments - use all columns
            columns = None
        elif len(items) == 1:
            # use with column list or limit
            arg = items[0]
            if arg is None:
                # use with no arguments (optional use_list was None)
                columns = None
            elif isinstance(arg, int) or (
                hasattr(arg, "value") and isinstance(arg.value, (int, float))
            ):
                # It's a limit
                columns = None
            else:
                # It's a column list
                columns = arg if isinstance(arg, list) else [arg]
        else:
            # use with both columns and limit
            columns = items[0] if isinstance(items[0], list) else [items[0]]

        return Use(columns)

    def use_list(self, items):
        """Transform use list."""
        return items

    def use_item(self, items):
        """Transform use item."""
        if len(items) == 1:
            # Just an expression
            return (items[0], None)
        # Expression with alias: expr AS alias
        return (items[0], items[1])

    def map_stmt(self, items: List[Any]) -> Map:
        """Transform map statement."""
        # items[0] should be a list of field mappings
        mappings = {}
        if isinstance(items[0], list):
            for mapping in items[0]:
                if isinstance(mapping, tuple) and len(mapping) == 2:
                    old_name, new_name = mapping
                    mappings[old_name] = new_name
        return Map(mappings)

    def field_mapping(self, items):
        """Transform field mapping."""
        return (items[0], items[1])

    def group_stmt(self, items):
        """Transform group statement."""
        # According to grammar: "group" field_list ["having" condition]
        # items[0] is field_list (list of field names)
        # items[1] is optional having condition (if present)
        by_fields = items[0] if items[0] else []

        # For now, create empty aggs - this might need to be handled differently
        # The aggregations are probably specified in the USE statement
        aggs = {}

        # Check if there's a HAVING condition
        having_condition = None
        if len(items) > 1 and items[1] is not None:
            having_condition = items[1]

            # Extract aggregation functions from the HAVING condition
            # and automatically add them to aggs
            aggs.update(self._extract_aggs_from_condition(having_condition))

        # If there's a HAVING clause, we need to return both Group and Having steps
        if having_condition:
            return [Group(by_fields, aggs), Having(having_condition)]
        return Group(by_fields, aggs)

    def _extract_aggs_from_condition(self, condition):
        """Extract aggregation functions from a condition and return aggs dict."""
        aggs = {}

        def find_agg_funcs(node):
            if hasattr(node, "name") and hasattr(node, "arg"):
                # This is an AggFunc node
                func_name = normalize_token(node.name).lower()
                if func_name in ["count", "sum", "avg", "min", "max"]:
                    if (
                        hasattr(node.arg, "raw")
                        and normalize_token(node.arg.raw) == "*"
                    ):
                        agg_key = f"{normalize_token(node.name)}(*)"
                    else:
                        agg_key = f"{normalize_token(node.name)}({node.arg})"
                    aggs[agg_key] = node
            elif hasattr(node, "left") and hasattr(node, "right"):
                # This is a BinaryOp, recurse on both sides
                find_agg_funcs(node.left)
                find_agg_funcs(node.right)
            elif hasattr(node, "children"):
                # This is a Tree node, recurse on children
                for child in node.children:
                    find_agg_funcs(child)

        find_agg_funcs(condition)
        return aggs

    def agg_mapping(self, items):
        """Transform aggregation mapping."""
        return (items[0], items[1])

    def agg_func(self, items):
        """Transform aggregation function."""
        func_name = items[0]
        if len(items) > 1:
            arg = items[1]
        else:
            # Default argument for count() etc.
            arg = Var("*")
        return AggFunc(func_name, arg)

    def save_stmt(self, items):
        """Transform save statement."""
        return Save(items[0])

    def let_stmt(self, items):
        """Transform let statement."""
        # items[0] is variable name, items[1] is the source
        var_name = items[0]
        if isinstance(var_name, Token):
            var_name = str(var_name.value)
        elif hasattr(var_name, "value"):
            var_name = str(var_name.value)
        else:
            var_name = str(var_name)

        source = items[1]
        return Let(var_name, source)
