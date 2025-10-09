"""
Pipeline and data source transformers for AST transformation.

This module contains transformers for pipeline construction and data source handling.
"""

from typing import List, Any
from lark import Token

from ..ast import Pipeline, From
from .utils import parse_source_with_alias


class PipelineTransformers:
    """Mixin class for pipeline transformation methods."""

    def start(self, items):
        """Transform start rule."""
        # items contains all the pipelines
        if len(items) == 1:
            return items[0]
        return items

    def pipeline(self, items):
        """Transform pipeline."""
        steps = []

        # Check if the first item is a from_stmt
        start_idx = 0
        if (
            items
            and hasattr(items[0], "__class__")
            and items[0].__class__.__name__ == "From"
        ):
            # First step is a From statement
            steps.append(items[0])
            start_idx = 1

        # Add remaining steps
        for i in range(start_idx, len(items)):
            step = items[i]
            if step is not None:  # Skip None values
                steps.append(step)

        # If no From statement was found and we have steps,
        # the pipeline operates on the current data
        if not steps:
            return Pipeline([])

        return Pipeline(steps)

    def from_stmt(self, items):
        """Transform from statement."""
        source_info = items[0]

        # Handle source with possible alias
        source, alias = parse_source_with_alias(source_info)

        # Handle extra parameters if present
        extra_params = {}
        if len(items) > 1 and items[1] is not None:
            extra_params = items[1]

        return From(source=source, alias=alias, extra=extra_params)

    def source_with_alias(self, items):
        """Transform source with optional alias."""
        # items[0] is the source (file_name or VAR)
        # items[1] might be "as" keyword (if present)
        # items[2] might be the alias (if present)

        source = items[0]

        # Handle VAR tokens
        if hasattr(source, "value"):
            source = source.value
        elif hasattr(source, "type") and source.type == "VAR":
            source = str(source.value)

        # Check if there's an alias
        alias = None
        if len(items) >= 3:
            # items[1] should be "as", items[2] should be the alias
            alias_token = items[2]
            if hasattr(alias_token, "value"):
                alias = alias_token.value
            else:
                alias = str(alias_token)

        # Return tuple (source, alias) if alias exists, otherwise just source
        if alias:
            return (source, alias)
        return source

    def var_token(self, tok):
        """Transform VAR token."""
        return str(tok.value)

    # Lark compatibility alias
    VAR = var_token

    def extra_params(self, items):
        """Transform extra parameters."""
        params = {}
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                key, value = item
                params[key] = value
            elif isinstance(item, list):
                # If item is a list of tuples from param_list
                for pair in item:
                    if isinstance(pair, tuple) and len(pair) == 2:
                        key, value = pair
                        params[key] = value
        return params

    def param_list(self, items):
        """Transform parameter list."""
        # items contains all the param_pairs
        result = []
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                result.append(item)
        return result

    def param_pair(self, items):
        """Transform parameter pair."""
        # items[0] is key, items[1] is value
        key = items[0]
        value = items[1]

        # Handle token values
        if hasattr(key, "value"):
            key = key.value
        if hasattr(value, "value"):
            value = value.value

        return (str(key), str(value))

    def param_value(self, items):
        """Transform parameter value."""
        # items[0] contains the actual value (FILENAME, IDENT, NUMBER, etc.)
        value = items[0]
        if hasattr(value, "value"):
            return value.value
        return str(value)

    def file_name(self, items: List[Any]) -> str:
        """Transform file name."""
        if len(items) == 1:
            return self._parse_filename(items[0])
        # Multiple parts - join them
        parts = [self._parse_filename(item) for item in items]
        return "".join(parts)

    def escaped_string_token(self, tok: Token) -> str:
        """Transform escaped string token."""
        # Remove quotes and handle escape sequences
        s = tok.value[1:-1]  # Remove surrounding quotes
        # Basic escape sequence handling
        s = s.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
        s = s.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
        return s

    # Lark compatibility alias
    ESCAPED_STRING = escaped_string_token

    def squoted_string_token(self, tok: Token) -> str:
        """Transform single-quoted string token."""
        # Remove quotes but don't process escape sequences in single quotes
        s = tok.value[1:-1]  # Remove surrounding quotes
        return s

    # Lark compatibility alias
    SQUOTED_STRING = squoted_string_token

    def filename_token(self, tok: Token) -> str:
        """Transform filename token."""
        return str(tok.value)

    # Lark compatibility alias
    FILENAME = filename_token

    def _parse_filename(self, item: Any) -> str:
        """Parse filename from various token types."""
        if hasattr(item, "value"):
            return str(item.value)
        if isinstance(item, str):
            return item
        return str(item)

    def name_token(self, items: List[Any]) -> str:
        """Transform name token."""
        if hasattr(items[0], "value"):
            return str(items[0].value)
        return str(items[0])
