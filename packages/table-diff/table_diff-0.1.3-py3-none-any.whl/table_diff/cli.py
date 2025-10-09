"""CLI (Command Line Interface) entry point for table_diff."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import polars as pl
import typed_argparse as tap
from loguru import logger
from ordered_set import OrderedSet

from table_diff.pdf_export import export_markdown_to_pdf
from table_diff.report_common import DiffEvaluation
from table_diff.report_duckdb import export_duckdb_report
from table_diff.report_markdown import generate_markdown_report


def load_table(path: Path) -> pl.DataFrame:
    """Load a table from a CSV or Parquet file.

    Args:
        path (Path): The path to the file.

    Returns:
        pl.DataFrame: The loaded DataFrame.

    Raises:
        ValueError: If the file format is not supported.

    """
    if path.suffix.lower() == ".csv":
        return pl.read_csv(
            path,
            infer_schema_length=None,  # Force using the entire file for schema inference.
        )
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pl.read_parquet(path)

    # Else:
    msg = f"Unsupported file format: {path.suffix}"
    raise ValueError(msg)


class Args(tap.TypedArgs):
    """CLI arguments for table_diff."""

    old_path: Path = tap.arg(
        "--old",
        positional=True,
        help="Path to the old CSV/Parquet table.",
    )
    new_path: Path = tap.arg(
        "--new",
        positional=True,
        help="Path to the new CSV/Parquet table.",
    )
    unique_key: list[str] | None = tap.arg(
        "-u",
        "--unique-key",
        nargs="*",
        help="Column(s) that form a unique key for the DataFrames.",
    )
    output_markdown_path: Path | None = tap.arg(
        "--md",
        "--markdown",
        "--output",
        help="Optional path to save the report. If not provided, the report is printed to stdout.",
    )
    output_pdf_path: Path | None = tap.arg(
        "--pdf",
        help="Optional path to save the report as a PDF. If not provided, PDF is not generated.",
    )
    force_stdout: bool = tap.arg(
        "--stdout",
        help="Force output to stdout, even if --md is provided.",
    )
    output_duckdb_path: Path | None = tap.arg(
        "--duckdb",
        help="Optional path to save all the data as a DuckDB database.",
    )
    enable_debug_logging: bool = tap.arg(
        "--debug",
        help="Enable debug logging.",
    )


def runner(args: Args) -> None:
    """Run the main application with the provided arguments.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    """
    # Configure logging.
    logger.remove()
    if args.enable_debug_logging:
        logger.add(sys.stderr, level="DEBUG")
        logger.debug("Enabled debug logging.")

    start_time = datetime.now(timezone.utc)

    path_old = args.old_path
    path_new = args.new_path

    if not path_old.exists():
        msg = f"File not found: {path_old}"
        raise FileNotFoundError(msg)
    if not path_new.exists():
        msg = f"File not found: {path_new}"
        raise FileNotFoundError(msg)

    df_old = load_table(path_old)
    logger.debug(f"Loaded old table: {df_old.shape} = {df_old.estimated_size('gb'):.1f} GB")
    df_new = load_table(path_new)
    logger.debug(f"Loaded new table: {df_new.shape} = {df_new.estimated_size('gb'):.1f} GB")

    if (args.unique_key is None) or (len(args.unique_key) == 0):
        # No unique key provided. For now, just print the common columns and exit.
        # TODO: Could try to automatically-detect columns by working lef-to-right.
        common_cols = OrderedSet(df_new.columns) & OrderedSet(df_old.columns)
        sys.stderr.write("No unique key provided. Columns present in both tables:\n\n")
        sys.stderr.write(json.dumps(list(common_cols)))
        sys.stderr.write("\n\n")
        sys.stderr.write("Please provide a unique key using: -u col1 col2")
        sys.stderr.write("\n")
        sys.exit(3)

    else:  # `unique_key` is provided.
        unique_key: list[str] = args.unique_key

    # Calculate the overall diff.
    diff_evaluation = DiffEvaluation.evaluate(
        df_old,
        df_new,
        unique_key=unique_key,
        old_filename=path_old.name,
        new_filename=path_new.name,
    )

    diff_evaluation_duration = datetime.now(timezone.utc) - start_time
    logger.debug(f"Reading file and diff evaluation took: {diff_evaluation_duration}")

    md_report = generate_markdown_report(diff_evaluation)

    if args.output_markdown_path:
        args.output_markdown_path.write_text(md_report)

    if (not args.output_markdown_path) or args.force_stdout:
        sys.stdout.write(md_report)

    if args.output_pdf_path:
        export_markdown_to_pdf(md_report, args.output_pdf_path)

    if args.output_duckdb_path:
        args.output_duckdb_path.unlink(missing_ok=True)
        export_duckdb_report(diff_evaluation, args.output_duckdb_path)

        # Print out the path for easy copying to DBeaver, etc.
        sys.stderr.write(f"DuckDB database saved to: {args.output_duckdb_path.absolute()}\n")

    total_duration = datetime.now(timezone.utc) - start_time
    logger.debug(f"Total time: {total_duration}")


def main() -> None:
    """CLI entry point for table_diff."""
    tap.Parser(Args).bind(runner).run()


if __name__ == "__main__":
    main()
