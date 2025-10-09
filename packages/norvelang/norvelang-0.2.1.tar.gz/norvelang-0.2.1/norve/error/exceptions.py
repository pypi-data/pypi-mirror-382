"""
Comprehensive error classes for Norvelang.
Provides detailed error messages with context and suggestions.
"""

import difflib
from ..token_utils import normalize_token


class NorvelangError(Exception):
    """Base class for all Norvelang errors."""

    def __init__(self, message, block_num=None, block_str=None, suggestions=None):
        super().__init__(message)
        self.message = message
        self.block_num = block_num
        self.block_str = block_str
        self.suggestions = suggestions or []


class NorvelangSyntaxError(NorvelangError):
    """Syntax errors in Norvelang code."""


class FileError(NorvelangError):
    """File-related errors (not found, permission, format)."""

    def __init__(self, filename, message, suggestions=None):
        self.filename = filename
        super().__init__(
            f"File error with '{filename}': {message}", suggestions=suggestions
        )


class DataError(NorvelangError):
    """Data-related errors (invalid data, type mismatches, etc.)."""


class JoinError(NorvelangError):
    """Join operation errors."""

    def __init__(
        self, message, left_columns=None, right_columns=None, suggestions=None
    ):
        self.left_columns = left_columns
        self.right_columns = right_columns

        if not suggestions and left_columns and right_columns:
            suggestions = []
            # Suggest common column names
            common = set(left_columns) & set(right_columns)
            if common:
                suggestions.append(
                    f"Available common columns: {', '.join(sorted(common))}"
                )

            # Suggest case-insensitive matches
            left_lower = {col.lower(): col for col in left_columns}
            right_lower = {col.lower(): col for col in right_columns}
            case_matches = set(left_lower.keys()) & set(right_lower.keys())
            if case_matches:
                suggestions.append(
                    f"Case-insensitive matches found: {', '.join(sorted(case_matches))}"
                )

        super().__init__(message, suggestions=suggestions)


class AggregationError(NorvelangError):
    """Aggregation and grouping errors."""


class VariableError(NorvelangError):
    """Variable and reference errors."""

    def __init__(self, variable_name, message, available_vars=None, suggestions=None):
        self.variable_name = variable_name
        self.available_vars = available_vars or []

        if not suggestions and available_vars:
            suggestions = []
            # Suggest similar variable names
            close_matches = difflib.get_close_matches(
                variable_name, available_vars, n=3
            )
            if close_matches:
                suggestions.append(f"Did you mean: {', '.join(close_matches)}?")
            suggestions.append(
                f"Available variables: {', '.join(sorted(available_vars))}"
            )

        super().__init__(
            f"Variable '{variable_name}': {message}", suggestions=suggestions
        )


class FunctionError(NorvelangError):
    """Function call errors."""

    def __init__(
        self, function_name, message, available_functions=None, suggestions=None
    ):
        self.function_name = function_name
        self.available_functions = available_functions or []

        if not suggestions and available_functions:
            suggestions = []
            # Suggest similar function names
            normalized_function_name = normalize_token(function_name)
            close_matches = difflib.get_close_matches(
                normalized_function_name, available_functions, n=3
            )
            if close_matches:
                suggestions.append(f"Did you mean: {', '.join(close_matches)}?")
            suggestions.append(
                f"Available functions: {', '.join(sorted(available_functions))}"
            )

        super().__init__(
            f"Function '{normalize_token(function_name)}': {message}",
            suggestions=suggestions,
        )


class TypeMismatchError(NorvelangError):
    """Type mismatch errors in expressions."""

    def __init__(self, expected_type, actual_type, value=None, suggestions=None):
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.value = value

        message = f"Expected {expected_type}, got {actual_type}"
        if value is not None:
            message += f" (value: {repr(value)})"

        if not suggestions:
            suggestions = []
            if expected_type == "number" and actual_type == "string":
                suggestions.append(
                    "Try converting string to number: int(value) or float(value)"
                )
            elif expected_type == "string" and actual_type == "number":
                suggestions.append("Try converting number to string: str(value)")
            elif expected_type == "boolean":
                suggestions.append("Use comparison operators like ==, !=, <, >, <=, >=")

        super().__init__(message, suggestions=suggestions)


class ColumnError(NorvelangError):
    """Column-related errors."""

    def __init__(self, column_name, message, available_columns=None, suggestions=None):
        self.column_name = column_name
        self.available_columns = available_columns or []

        if not suggestions and available_columns:
            suggestions = []
            # Suggest similar column names
            close_matches = difflib.get_close_matches(
                column_name, available_columns, n=3
            )
            if close_matches:
                suggestions.append(f"Did you mean: {', '.join(close_matches)}?")

            # Check for case-insensitive matches
            lower_cols = {col.lower(): col for col in available_columns}
            if column_name.lower() in lower_cols:
                actual_col = lower_cols[column_name.lower()]
                suggestions.append(
                    f"Case mismatch: use '{actual_col}' instead of '{column_name}'"
                )

            suggestions.append(
                f"Available columns: {', '.join(sorted(available_columns))}"
            )

        super().__init__(f"Column '{column_name}': {message}", suggestions=suggestions)


class DivisionByZeroError(NorvelangError):
    """Division by zero errors."""

    def __init__(self, expression=None):
        message = "Division by zero"
        if expression:
            message += f" in expression: {expression}"

        suggestions = [
            "Check that denominator values are not zero",
            "Use conditional logic to avoid division by zero",
            "Consider using CASE/WHEN or WHERE clauses to filter out zero values",
        ]

        super().__init__(message, suggestions=suggestions)


class ComputationOverflowError(NorvelangError):
    """Computation overflow or excessive resource usage errors."""

    def __init__(self, expression=None, operation=None):
        if operation == "exponentiation":
            message = "Exponentiation would consume excessive resources"
            suggestions = [
                "Use smaller exponent values (limit: 1000)",
                "Use smaller base values for large exponents",
                "Consider using logarithmic operations for very large calculations",
            ]
        elif operation == "large_number":
            message = "Number too large for safe computation"
            suggestions = [
                "Use smaller numbers in calculations",
                "Break down large computations into smaller steps",
                "Consider using approximations for very large values",
            ]
        else:
            message = "Computation would consume excessive resources"
            suggestions = [
                "Use smaller values in calculations",
                "Avoid operations that could cause resource exhaustion",
            ]

        if expression:
            message += f" in expression: {expression}"

        super().__init__(message, suggestions=suggestions)


class LimitError(NorvelangError):
    """Limit clause errors."""

    def __init__(self, limit_value, message=None):
        self.limit_value = limit_value
        msg = message or f"Invalid limit value: {limit_value}"

        suggestions = ["Limit must be a positive integer", "Example: limit 10"]

        super().__init__(msg, suggestions=suggestions)


class OrderError(NorvelangError):
    """Order clause errors."""


class PipelineError(NorvelangError):
    """Pipeline structure errors."""
