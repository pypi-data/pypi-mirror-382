"""Tools to generate a plain text/markdown diff report for table_diff."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

from typing import TYPE_CHECKING

from table_diff.df_helpers import df_to_markdown

# TODO: from table_diff.diff_evaluate import regroup_column_diffs_by_type
from table_diff.report_common import DiffEvaluation

if TYPE_CHECKING:
    from table_diff.diff_types import ColumnDiff


def generate_markdown_report(
    diff_evaluation: DiffEvaluation,
    # TODO: Add settings about which diff types to include, etc.
) -> str:
    """Generate a plain text report of the differences between two tables.

    Returns:
        A string representation of the differences between the two tables.

    """
    unique_key = diff_evaluation.unique_key
    old_filename = diff_evaluation.old_filename
    new_filename = diff_evaluation.new_filename

    compare_unique_key_result = diff_evaluation.compare_unique_key_result
    compare_cols_result = diff_evaluation.compare_cols_result
    column_diffs: dict[str, ColumnDiff] = diff_evaluation.column_diffs
    general_observations = diff_evaluation.general_observations

    lines = [
        "# Comparison of the two tables",
        "",
        f"* Comparing `{old_filename}` (old, left) to `{new_filename}` (new, right)",
        # Hide: f"* Columns to compare: {compare_cols_result.compare_cols}",
    ]

    if len(unique_key) == 1:
        lines.append(f"* Unique key: `{unique_key[0]}`")
    else:
        lines.append(f"* Unique key ({len(unique_key)} columns):")
        lines.extend([f"    * `{col}`" for col in unique_key])

    lines.append("")

    # General observations
    lines.extend(["## General Observations", ""])
    if general_observations:
        lines.extend([f"* {observation}" for observation in general_observations])
    else:
        lines.append("No general observations.")

    # Columns in both
    lines.extend(["", "## Column Comparison", ""])

    lines.append(f"### Columns in both tables [{len(compare_cols_result.cols_in_both)} cols]")
    for col in compare_cols_result.cols_in_both:
        if col in unique_key:
            lines.append(f"* `{col}` (Unique Key)")
        else:
            lines.append(f"* `{col}` ({column_diffs[col].row_difference_description})")
    lines.append("")  # noqa: FURB113

    # Columns in old only
    lines.append(
        "### Columns in old table only (DROPPED) "
        f"[{len(compare_cols_result.cols_in_old_only)} cols]"
    )
    lines.extend([f"* `{col}`" for col in compare_cols_result.cols_in_old_only] + [""])

    # Columns in new only
    lines.append(
        f"### Columns in new table only (ADDED) [{len(compare_cols_result.cols_in_new_only)} cols]"
    )
    lines.extend([f"* `{col}`" for col in compare_cols_result.cols_in_new_only] + [""])

    # Rows
    lines.extend(["## Row Comparison (Unique Key)", ""])
    lines.extend(
        [
            f"* Rows in old: {diff_evaluation.df_old.height:,}",
            f"* Rows in new: {diff_evaluation.df_new.height:,}",
            f"* Rows added (new only): {compare_unique_key_result.rows_added_count:,}",
            f"* Rows removed (old only): {compare_unique_key_result.rows_removed_count:,}",
            f"* Rows in both: {compare_unique_key_result.rows_in_both_sides_count:,}",
            "",
        ]
    )

    # Add three sub-tables: rows added, rows removed, rows in both.
    # Skip adding each table if there are no rows to show.
    lines.extend(
        [
            f"### Rows Added ({compare_unique_key_result.rows_added_count:,} rows)",
            f"{compare_unique_key_result.rows_added_count:,} rows added.",
        ]
    )
    if compare_unique_key_result.rows_added_count > 0:
        lines.append(df_to_markdown(compare_unique_key_result.df_rows_added))
    lines.extend(
        [
            "",
            f"### Rows Removed ({compare_unique_key_result.rows_removed_count:,} rows)",
            f"{compare_unique_key_result.rows_removed_count:,} rows removed.",
        ]
    )
    if compare_unique_key_result.rows_removed_count > 0:
        lines.append(df_to_markdown(compare_unique_key_result.df_rows_removed))
    lines.extend(
        [
            "",
            f"### Rows in Both ({compare_unique_key_result.rows_in_both_sides_count:,} rows)",
            f"{compare_unique_key_result.rows_in_both_sides_count:,} rows in both old and new.",
        ]
    )
    if compare_unique_key_result.rows_in_both_sides_count > 0:
        lines.append(df_to_markdown(compare_unique_key_result.df_unique_key_in_both))
    lines.extend([""])

    # TODO: Use this: regroup_column_diffs_by_type(column_diffs)

    # Column diffs
    lines.extend(["## Column Diffs", ""])
    for col_diff in column_diffs.values():
        lines.extend(col_diff.to_markdown_str().splitlines())
        lines.append("")

    lines.extend(["", ""])

    # TODO: Could do the join with a system-specific newline character selection.
    return "\n".join(lines)
