"""Tools to compare two tables, and see the changes/types of changes between them."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import polars as pl
from loguru import logger

from table_diff.df_helpers import assert_col_has_no_nulls, assert_unique_key
from table_diff.diff_types import ColumnDiff, CompareColsResult, CompareUniqueKeyResult

POLARS_UNSORTABLE_TYPES = {pl.List, pl.Object, pl.Struct}


def assert_df_ready_for_compare(df: pl.DataFrame, unique_key: list[str]) -> None:
    """Assert that the unique_key is good, that it contains no nulls, and that it has rows.

    Args:
        df: The DataFrame to check.
        unique_key: The column(s) that should be unique.

    Raises:
        AssertionError: If the check fails.

    """
    assert_unique_key(df, unique_key)

    for col in unique_key:
        assert_col_has_no_nulls(df, col)

    if df.height == 0:
        msg = "df has 0 rows"
        raise AssertionError(msg)


def compare_for_general_observations(
    df_old: pl.DataFrame,
    df_new: pl.DataFrame,
    *,
    unique_key: list[str],
    compare_cols_result: CompareColsResult | None,
    compare_unique_key_result: CompareUniqueKeyResult | None,
) -> list[str]:
    """Create a list of general observations for generally very-similar diffs.

    Returns:
        A list of general observations about the differences between the two tables.

    """
    if compare_cols_result is None:
        compare_cols_result = CompareColsResult.evaluate(df_old, df_new, unique_key=unique_key)

    if compare_unique_key_result is None:
        compare_unique_key_result = CompareUniqueKeyResult.evaluate(
            df_old, df_new, unique_key=unique_key
        )

    generic_observations: list[str] = []

    assert_df_ready_for_compare(df_old, unique_key)
    assert_df_ready_for_compare(df_new, unique_key)

    # Order the cols: unique_key, cols_in_both, cols_in_[old_not_new/other]; sort by those cols
    df_old = df_old.select(
        unique_key + compare_cols_result.compare_cols + compare_cols_result.cols_in_old_only
    )
    df_new = df_new.select(
        unique_key + compare_cols_result.compare_cols + compare_cols_result.cols_in_new_only
    )

    df_old = df_old.sort(
        [
            col
            for col in df_old.columns
            if not any(isinstance(df_old[col].dtype, t) for t in POLARS_UNSORTABLE_TYPES)
        ]
    )
    df_new = df_new.sort(
        [
            col
            for col in df_new.columns
            if not any(isinstance(df_new[col].dtype, t) for t in POLARS_UNSORTABLE_TYPES)
        ]
    )

    if df_old.equals(df_new):
        generic_observations.append("Tables are perfectly equal after sort.")

    # Filter to only rows that are in both tables.
    # TODO: Performance - Could generate hashes of tables here instead of keeping both `.equals()`.
    df_old_cmp = df_old.select(compare_cols_result.cols_in_both).join(
        df_new.select(unique_key), on=unique_key, how="inner", validate="1:1"
    )
    df_new_cmp = df_new.select(compare_cols_result.cols_in_both).join(
        df_old.select(unique_key), on=unique_key, how="inner", validate="1:1"
    )

    # Validate overall system logic.
    assert len(df_old_cmp) == len(df_new_cmp), (
        "Error: df_old_cmp and df_new_cmp should have the same number of rows now, logical error"
    )
    assert len(df_old_cmp) == compare_unique_key_result.rows_in_both_sides_count, (
        "Error: df_old_cmp should have the same number of rows as pk_in_both_row_count, "
        "logical error"
    )

    # Good check
    if df_old_cmp.equals(df_new_cmp):
        generic_observations.append(
            "Tables are equal (after discarding added/removed rows, and after considering only "
            "the columns in both tables)."
        )
        # Could return early, no more value. Best to keep going for standard return value though.

    return generic_observations


def compare_each_column_into_table(
    df_old: pl.DataFrame,
    df_new: pl.DataFrame,
    *,
    unique_key: list[str],
    compare_cols_result: CompareColsResult | None,
) -> dict[str, ColumnDiff]:
    """Compare each column, returning a dict representing the comparison per-column.

    ColumnDiff contains a DataFrame of the differences, and some summary statistics.

    Returns:
        A dict of ColumnDiff objects, one per column.

    """
    if compare_cols_result is None:
        logger.debug("No CompareColsResult provided, calculating it now.")
        compare_cols_result = CompareColsResult.evaluate(df_old, df_new, unique_key=unique_key)

    results: dict[str, ColumnDiff] = {}

    # Compare the values in the columns
    for col in compare_cols_result.compare_cols:
        logger.debug(f'Comparing column: ColumnDiff.evaluate(column_name="{col}")')

        results[col] = ColumnDiff.evaluate(
            column_name=col,
            df_old=df_old,
            df_new=df_new,
            unique_key=unique_key,
        )

    return results


def regroup_column_diffs_by_type(status_col_lists: dict[str, ColumnDiff]) -> dict[str, list[str]]:
    """Regroup the column differences into a dict of counts per status.

    Returns
    -------
        A dict of counts per status, where each status (key) is like "No rows differ.", and the
        values are lists of column names.

    """
    # Values will be the num of cols.
    col_status_counts: dict[str, list[str]] = {
        "No rows differ.": [],
        "Some rows differ.": [],
        "All rows differ.": [],
    }

    for status in col_status_counts:  # noqa: PLC0206
        for col_name, col_diff in status_col_lists.items():
            if col_diff.row_difference_summary == status:
                col_status_counts[status].append(col_name)

    return col_status_counts
