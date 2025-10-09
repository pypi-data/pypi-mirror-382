"""Tool for generating a DuckDB database representing the differences between two tables."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import re
from pathlib import Path

import duckdb
import polars as pl

from table_diff.report_common import DiffEvaluation


def _create_duckdb_table_from_df(
    duckdb_path: Path,
    table_name: str,
    df: pl.DataFrame,
) -> None:
    """Create a DuckDB table from a Polars DataFrame.

    Args:
        duckdb_path: The path to the DuckDB database.
        table_name: The name of the table to create.
        df: The DataFrame to use as the table.

    """
    assert isinstance(df, pl.DataFrame)

    table_name = re.sub(r"[^a-zA-Z0-9_]+", "_", table_name)

    # Create the DuckDB table.
    with duckdb.connect(duckdb_path, read_only=False) as conn:  # pyright: ignore[reportUnknownMemberType]
        # Note: The following line uses magic to read the `df` local variable, as it's mentioned
        # in the SQL query.
        conn.execute(f"""CREATE TABLE '{table_name}' AS SELECT * FROM df""")  # noqa: S608


def export_duckdb_report(
    diff_evaluation: DiffEvaluation,
    output_duckdb_path: Path,
) -> None:
    """Generate a DuckDB database representing the differences between two DataFrames.

    Args:
        diff_evaluation: The result of the diff evaluation.
        output_duckdb_path: The path to save the DuckDB database.

    """
    # Create the tables.
    _create_duckdb_table_from_df(output_duckdb_path, "010_old_table", diff_evaluation.df_old)
    _create_duckdb_table_from_df(output_duckdb_path, "011_new_table", diff_evaluation.df_new)

    # Create the general observations table.
    df_observations = pl.DataFrame(
        {
            "observation_number": list(range(1, len(diff_evaluation.general_observations) + 1)),
            "observation": diff_evaluation.general_observations,
        },
    )
    if df_observations.height > 0:
        _create_duckdb_table_from_df(
            output_duckdb_path, "012_general_observations", df_observations
        )

    # Create the diff tables (added/removed/common).
    _create_duckdb_table_from_df(
        output_duckdb_path,
        "020_rows_added",
        diff_evaluation.compare_unique_key_result.df_rows_added,
    )
    _create_duckdb_table_from_df(
        output_duckdb_path,
        "021_rows_removed",
        diff_evaluation.compare_unique_key_result.df_rows_removed,
    )
    _create_duckdb_table_from_df(
        output_duckdb_path,
        "022_rows_in_both",
        diff_evaluation.compare_unique_key_result.df_unique_key_in_both,
    )

    # Create the column diff tables.
    for i, (col_name, col_diff) in enumerate(diff_evaluation.column_diffs.items()):
        if col_diff.row_difference_count == 0:
            continue

        pct_diff = (col_diff.row_difference_count / diff_evaluation.df_old.height) * 100

        if col_diff.df_diff_full is not None:
            _create_duckdb_table_from_df(
                output_duckdb_path,
                f"{100 + i}_{col_name}_diff_{pct_diff:.0f}_pct",
                col_diff.df_diff_full,
            )
        else:
            _create_duckdb_table_from_df(
                output_duckdb_path,
                f"{100 + i}_{col_name}_diff_sample_{pct_diff:.0f}_pct",
                col_diff.df_diff_sample,
            )
