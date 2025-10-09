"""
Result types for Norvelang API.

This module contains the NorvelangResult class and related utilities.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class ResultConfig:
    """Configuration for NorvelangResult."""
    dataframes: List[pd.DataFrame] = None
    variables: Dict[str, Any] = None
    stdout: str = ""
    success: bool = True
    errors: List[str] = None


class NorvelangResult:
    """Container for Norvelang execution results."""

    def __init__(self, **kwargs):
        """Initialize with keyword arguments or config object."""
        if len(kwargs) == 1 and isinstance(list(kwargs.values())[0], ResultConfig):
            config = list(kwargs.values())[0]
            self.dataframes = config.dataframes or []
            self.variables = config.variables or {}
            self.stdout = config.stdout
            self.success = config.success
            self.errors = config.errors or []
        else:
            self.dataframes = kwargs.get('dataframes', []) or []
            self.variables = kwargs.get('variables', {}) or {}
            self.stdout = kwargs.get('stdout', "")
            self.success = kwargs.get('success', True)
            self.errors = kwargs.get('errors', []) or []

    def __repr__(self):
        return (
            "NorvelangResult("
            f"dataframes={len(self.dataframes)}, "
            f"variables={len(self.variables)}, "
            f"success={self.success})"
        )

    def get_first_dataframe(self):
        """Get the first DataFrame, or None if no DataFrames exist."""
        return self.dataframes[0] if self.dataframes else None

    def has_errors(self):
        """Check if the result contains any errors."""
        return bool(self.errors) or not self.success

    def get_error_summary(self):
        """Get a summary of all errors."""
        if not self.has_errors():
            return "No errors"

        error_parts = []
        if not self.success:
            error_parts.append("Execution failed")
        if self.errors:
            error_parts.extend(self.errors)

        return "; ".join(error_parts)
