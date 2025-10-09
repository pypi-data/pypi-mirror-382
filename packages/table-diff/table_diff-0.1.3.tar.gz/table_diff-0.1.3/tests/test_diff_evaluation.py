"""Unit tests for the `DiffEvaluation` class."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import tempfile
from pathlib import Path

import polars as pl

from table_diff.pdf_export import export_markdown_to_pdf
from table_diff.report_common import DiffEvaluation
from table_diff.report_duckdb import export_duckdb_report
from table_diff.report_markdown import generate_markdown_report


def test_diff_evaluation_runs() -> None:
    """Test that DiffEvaluation.evaluate runs without error on sample data."""
    data_folder = Path(__file__).parent / "demo_datasets/populations"
    assert data_folder.is_dir()

    df_old = pl.read_csv(path_old := data_folder / "city-populations_2010.csv")
    df_new = pl.read_csv(path_new := data_folder / "city-populations_2015.csv")

    _ = DiffEvaluation.evaluate(
        df_old,
        df_new,
        unique_key=["location_id"],
        old_filename=path_old.name,
        new_filename=path_new.name,
    )


def test_diff_evaluation_and_conversions_run() -> None:
    """Test that DiffEvaluation and report exports run without error on sample data.

    This test is more of an integration test than a unit test, as it checks many functions
    sequentially.
    """
    data_folder = Path(__file__).parent / "demo_datasets/populations"
    assert data_folder.is_dir()

    df_old = pl.read_csv(path_old := data_folder / "city-populations_2010.csv")
    df_new = pl.read_csv(path_new := data_folder / "city-populations_2015.csv")

    diff_evaluation = DiffEvaluation.evaluate(
        df_old,
        df_new,
        unique_key=["location_id"],
        old_filename=path_old.name,
        new_filename=path_new.name,
    )

    md_report = generate_markdown_report(diff_evaluation)
    assert len(md_report) > 1000

    with tempfile.TemporaryDirectory() as temp_dir:
        export_markdown_to_pdf(md_report, Path(temp_dir) / "report.pdf")
        export_duckdb_report(diff_evaluation, Path(temp_dir) / "report.duckdb")
