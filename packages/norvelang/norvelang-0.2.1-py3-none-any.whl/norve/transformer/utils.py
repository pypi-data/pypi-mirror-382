"""
Utility functions for AST transformation.

This module contains shared utility functions used by transformer modules,
separated to avoid cyclic import issues.
"""


def parse_source_with_alias(source_info):
    """
    Parse source information that may contain an alias.

    Args:
        source_info: Either a source object or tuple of (source, alias)

    Returns:
        Tuple of (source, alias) where alias may be None
    """
    if isinstance(source_info, tuple):
        source, alias = source_info
    else:
        source = source_info
        alias = None
    return source, alias
