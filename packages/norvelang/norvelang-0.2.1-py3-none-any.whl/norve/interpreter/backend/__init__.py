"""
Backend package for norvelang interpreter.

This package provides the backend implementation split into focused modules:
- core: Main ListBackend class
- column_utils: Column resolution and utilities
- joins: Join operations
- display: Show and display functionality
- grouping: Group operations and aggregations
"""

from .core import ListBackend

__all__ = ["ListBackend"]
