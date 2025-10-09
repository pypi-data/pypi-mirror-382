"""
norvelang CLI entry point
"""

import sys
import argparse
from .run_pipe import run_pipeline
from .repl import repl






def main():
    """Main CLI for norvelang. Reads a pipeline file and executes it, or starts REPL."""
    parser = argparse.ArgumentParser(description="norvelang CLI")
    parser.add_argument("pipeline_file", nargs="?", help="Pipeline file to execute")
    parser.add_argument(
        "-c",
        "--command",
        type=str,
        help="Execute norvelang code directly from command line",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=10,
        help="Row limit if no explicit limit is set",
    )
    parser.add_argument(
        "--internal-errors",
        action="store_true",
        help="Show internal error details for debugging",
    )
    cython_group = parser.add_mutually_exclusive_group()
    cython_group.add_argument(
        "--no-lark-cython",
        action="store_true",
        help="Force use of regular lark parser",
    )
    args = parser.parse_args()

    # Handle -c/--command flag for direct code execution
    if args.command:
        pipeline = args.command
        use_cython = not args.no_lark_cython
        run_pipeline(
            pipeline,
            default_limit=args.limit,
            show_internal_errors=args.internal_errors,
            use_cython=use_cython,
        )
        return

    if not args.pipeline_file:
        repl(default_limit=args.limit)
        return
    pipeline_path = args.pipeline_file
    default_limit = args.limit
    try:
        with open(pipeline_path, encoding="utf-8") as f:
            pipeline = f.read()
    except (FileNotFoundError, OSError, UnicodeDecodeError) as e:
        print(f"Error reading {pipeline_path}: {e}")
        sys.exit(1)
    if not pipeline.strip():
        return
    use_cython = not args.no_lark_cython
    run_pipeline(
        pipeline,
        default_limit=default_limit,
        show_internal_errors=args.internal_errors,
        use_cython=use_cython,
    )


if __name__ == "__main__":
    main()
