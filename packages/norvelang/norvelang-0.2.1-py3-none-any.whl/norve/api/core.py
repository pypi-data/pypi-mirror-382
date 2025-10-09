"""
Core Norvelang API functions.

This module provides the main entry points for executing Norvelang code
and getting results as DataFrames or stdout output.
"""

from typing import Union, Dict, List, Optional, Any
import pandas as pd
from lark import LarkError

from ..error.block_split import split_blocks
from ..error.exceptions import NorvelangError
from ..run_pipe import run_pipe
from ..parser import parse
from ..interpreter.backend import ListBackend

from .utils import capture_stdout, filter_empty_blocks
from .result_types import NorvelangResult
from .dataframe_capture import DataFrameCapture


def execute_with_output(
    code: str, variables: Optional[Dict[str, Any]] = None, default_limit: int = 10
) -> str:
    """
    Execute Norvelang code and return the stdout output as a string.

    Args:
        code: Norvelang code to execute
        variables: Dictionary of variables to make available (let_tables)
        default_limit: Default row limit for queries

    Returns:
        String containing the captured stdout output
    """
    if variables is None:
        variables = {}
    else:
        variables = variables.copy()  # Don't modify the original

    # Capture stdout during execution
    with capture_stdout() as stdout_buffer:
        try:
            # Parse the code into blocks
            blocks = split_blocks(code)

            # Use shared block filtering utility
            for i, block_str in filter_empty_blocks(blocks):
                try:
                    # Parse the block
                    ast = parse(block_str)
                except Exception as e:
                    raise RuntimeError(f"Parse error in block {i+1}: {str(e)}") from e

                try:
                    # Execute the block
                    if isinstance(ast, list):
                        for pipe in ast:
                            run_pipe(pipe, variables, default_limit)
                    else:
                        run_pipe(ast, variables, default_limit)
                except (
                    LarkError,
                    NorvelangError,
                    ValueError,
                    TypeError,
                    KeyError,
                ) as e:
                    raise RuntimeError(f"Runtime error in block {i+1}: {str(e)}") from e

        except (RuntimeError, LarkError, NorvelangError) as e:
            print(f"Execution error: {str(e)}")

    return stdout_buffer.getvalue()


def execute_query(
    code: str, variables: Optional[Dict[str, Any]] = None, default_limit: int = 10
) -> pd.DataFrame:
    """
    Execute a Norvelang query and return the result as a pandas DataFrame.

    This function executes the query and captures the output table as a DataFrame.
    It works by temporarily replacing the use method to capture the DataFrame
    instead of printing it.

    Args:
        code: Norvelang query code
        variables: Dictionary of variables to make available
        default_limit: Default row limit for the query

    Returns:
        pandas DataFrame with the query results

    Raises:
        RuntimeError: If the query produces errors or doesn't return a table
    """
    if variables is None:
        variables = {}
    else:
        variables = variables.copy()  # Don't modify the original

    # Create DataFrame capture instance
    capture = DataFrameCapture()

    # Replace the use method temporarily
    original_use = ListBackend.use
    ListBackend.use = capture.create_capture_use_method()

    try:
        # Parse the code into blocks
        blocks = split_blocks(code)

        for i, block in enumerate(blocks):
            block_str = block.strip()
            if not block_str:
                continue

            try:
                # Parse the block
                ast = parse(block_str)
            except Exception as e:
                raise RuntimeError(f"Parse error in block {i+1}: {str(e)}") from e

            try:
                # Execute the block
                if isinstance(ast, list):
                    for pipe in ast:
                        run_pipe(pipe, variables, default_limit)
                else:
                    run_pipe(ast, variables, default_limit)
            except Exception as e:
                raise RuntimeError(f"Runtime error in block {i+1}: {str(e)}") from e

    finally:
        # Restore the original use method
        ListBackend.use = original_use

    if len(capture.captured_dfs) == 0:
        raise RuntimeError("Query did not produce any results")
    if len(capture.captured_dfs) == 1:
        return capture.captured_dfs[0]
    # If multiple DataFrames were captured, return the last one
    return capture.captured_dfs[-1]


def _process_block(block_str: str, variables: dict, default_limit: int):
    """Process a single code block."""
    ast = parse(block_str)
    if isinstance(ast, list):
        for pipe in ast:
            run_pipe(pipe, variables, default_limit)
    else:
        run_pipe(ast, variables, default_limit)


def _execute_with_dataframes_and_output(
    code: str, variables: dict, default_limit: int
) -> NorvelangResult:
    """Execute code capturing both DataFrames and stdout output."""
    capture = DataFrameCapture()
    original_use = ListBackend.use
    ListBackend.use = capture.create_capture_use_method()

    errors = []
    success = True

    try:
        with capture_stdout() as stdout_buffer:
            blocks = split_blocks(code)
            for i, block in enumerate(blocks):
                block_str = block.strip()
                if not block_str:
                    continue
                try:
                    _process_block(block_str, variables, default_limit)
                except (
                    LarkError,
                    NorvelangError,
                    ValueError,
                    TypeError,
                    KeyError,
                ) as e:
                    errors.append(f"Block {i+1}: {str(e)}")
                    success = False
        stdout_output = stdout_buffer.getvalue()
    finally:
        ListBackend.use = original_use

    return NorvelangResult(
        dataframes=capture.captured_dfs,
        variables=variables,
        stdout=stdout_output,
        success=success,
        errors=errors,
    )


def _execute_with_dataframes_only(
    code: str, variables: dict, default_limit: int
) -> List[pd.DataFrame]:
    """Execute code capturing only DataFrames."""
    try:
        result_df = execute_query(code, variables, default_limit)
        return [result_df]
    except (LarkError, NorvelangError, ValueError, TypeError):
        return []


def _execute_with_output_only(code: str, variables: dict, default_limit: int) -> str:
    """Execute code capturing only stdout output."""
    try:
        return execute_with_output(code, variables, default_limit)
    except (LarkError, NorvelangError, ValueError, TypeError):
        return ""


def _execute_without_capture(code: str, variables: dict, default_limit: int) -> bool:
    """Execute code without capturing output, return success status."""
    errors = []
    try:
        blocks = split_blocks(code)
        for i, block in enumerate(blocks):
            block_str = block.strip()
            if not block_str:
                continue
            try:
                ast = parse(block_str)
                if isinstance(ast, list):
                    for pipe in ast:
                        run_pipe(pipe, variables, default_limit)
                else:
                    run_pipe(ast, variables, default_limit)
            except (LarkError, NorvelangError, ValueError, TypeError, KeyError) as e:
                errors.append(f"Block {i+1}: {str(e)}")
                return False
    except (LarkError, NorvelangError, ValueError, TypeError):
        return False
    return True


def execute(
    code: str,
    variables: Optional[Dict[str, Any]] = None,
    default_limit: int = 10,
    return_dataframes: bool = True,
    capture_output: bool = False,
) -> Union[List[pd.DataFrame], str, NorvelangResult]:
    """
    Execute Norvelang code and return results in the specified format.

    This is the most flexible execution function, allowing you to choose
    what type of output you want.

    Args:
        code: Norvelang code to execute
        variables: Dictionary of variables to make available
        default_limit: Default row limit for queries
        return_dataframes: Whether to capture and return DataFrames
        capture_output: Whether to capture and return stdout

    Returns:
        - If return_dataframes=True and capture_output=False: List[DataFrame]
        - If return_dataframes=False and capture_output=True: str
        - If both are True: NorvelangResult object with both
        - If both are False: None (just executes the code)
    """
    if variables is None:
        variables = {}
    else:
        variables = variables.copy()

    try:
        return _execute_with_options(
            code, variables, default_limit, return_dataframes, capture_output
        )
    except (LarkError, NorvelangError, ValueError, TypeError) as e:
        return _handle_execution_error(e, variables, return_dataframes, capture_output)


def _execute_with_options(
    code: str,
    variables: dict,
    default_limit: int,
    return_dataframes: bool,
    capture_output: bool,
):
    """Execute code with the specified options."""
    if return_dataframes and capture_output:
        # Need both DataFrames and stdout - capture both
        return _execute_with_dataframes_and_output(code, variables, default_limit)

    if return_dataframes:
        # Only need DataFrames
        return _execute_with_dataframes_only(code, variables, default_limit)

    if capture_output:
        # Only need stdout
        return _execute_with_output_only(code, variables, default_limit)

    # Just execute, don't return anything
    _execute_without_capture(code, variables, default_limit)
    return None


def _handle_execution_error(
    error, variables: dict, return_dataframes: bool, capture_output: bool
):
    """Handle execution errors and return appropriate error response."""
    if return_dataframes and capture_output:
        return NorvelangResult(
            dataframes=[],
            variables=variables,
            stdout="",
            success=False,
            errors=[str(error)],
        )
    if return_dataframes:
        return []
    if capture_output:
        return ""
    return None
