"""
REPL (Read-Eval-Print Loop) module for interactive Norvelang sessions.

Provides an interactive command-line interface for executing Norvelang pipelines.
"""
from lark import LarkError
from .error.exceptions import NorvelangError
from .run_pipe import run_pipeline


def repl(default_limit=10):
    """Start a norvelang REPL with simple input support."""
    print("norvelang REPL. Enter pipeline, press Enter to submit, 'exit' to exit.")
    let_tables = {}
    current_input = []

    while True:
        try:
            prompt = ">>> "
            line = input(prompt)

            if not line.strip():
                continue

            current_input.append(line)
            full_input = "\n".join(current_input)

            if full_input.strip().lower() == "exit":
                print("Exiting REPL.")
                break

            try:
                run_pipeline(full_input, let_tables, default_limit=default_limit)
            except (LarkError, NorvelangError, ValueError, TypeError, KeyError) as e:
                print(f"Error: {e}")

            # Reset for next input
            current_input = []

        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break
