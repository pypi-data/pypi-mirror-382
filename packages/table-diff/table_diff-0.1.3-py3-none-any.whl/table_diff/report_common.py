"""Tools to generate the overall diff report for table_diff."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

from dataclasses import dataclass

import polars as pl
from loguru import logger

from table_diff.diff_evaluate import (
    assert_df_ready_for_compare,
    compare_each_column_into_table,
    compare_for_general_observations,
)
from table_diff.diff_types import ColumnDiff, CompareColsResult, CompareUniqueKeyResult


@dataclass(kw_only=True)
class DiffEvaluation:
    """A report of the differences between two DataFrames, to be rendered into any form."""

    # Store the general input data.
    df_old: pl.DataFrame
    df_new: pl.DataFrame
    unique_key: list[str]
    old_filename: str | None = None
    new_filename: str | None = None

    # Store the results of the comparison.
    compare_unique_key_result: CompareUniqueKeyResult
    compare_cols_result: CompareColsResult
    column_diffs: dict[str, ColumnDiff]
    general_observations: list[str]

    @staticmethod
    def evaluate(
        df_old: pl.DataFrame,
        df_new: pl.DataFrame,
        *,
        unique_key: list[str],
        old_filename: str | None = None,
        new_filename: str | None = None,
        # TODO: Add settings about which diff types to include, etc.
    ) -> "DiffEvaluation":
        """Generate a memoized report of the differences between two DataFrames.

        Returns:
            A representation of the differences between the two DataFrames.

        """
        logger.debug('Starting "DiffEvaluation.evaluate()"')

        assert_df_ready_for_compare(df_old, unique_key=unique_key)
        assert_df_ready_for_compare(df_new, unique_key=unique_key)
        logger.debug('Done "assert_df_ready_for_compare()" validations.')

        logger.debug('Starting "CompareUniqueKeyResult.evaluate()"')
        compare_unique_key_result = CompareUniqueKeyResult.evaluate(
            df_old, df_new, unique_key=unique_key
        )
        logger.debug('Done "CompareUniqueKeyResult.evaluate()"')

        logger.debug('Starting "CompareColsResult.evaluate()"')
        compare_cols_result = CompareColsResult.evaluate(df_old, df_new, unique_key=unique_key)
        logger.debug('Done "CompareColsResult.evaluate()"')

        logger.debug('Starting "compare_each_column_into_table() -> ColumnDiff"')
        column_diffs: dict[str, ColumnDiff] = compare_each_column_into_table(
            df_old, df_new, unique_key=unique_key, compare_cols_result=compare_cols_result
        )
        logger.debug(
            f'Done "compare_each_column_into_table() -> ColumnDiff" '
            f"for {len(column_diffs.keys())} columns."
        )

        general_observations = compare_for_general_observations(
            df_old,
            df_new,
            unique_key=unique_key,
            compare_unique_key_result=compare_unique_key_result,
            compare_cols_result=compare_cols_result,
        )
        logger.debug('Done "compare_for_general_observations()"')

        return DiffEvaluation(
            df_old=df_old,
            df_new=df_new,
            unique_key=unique_key,
            old_filename=old_filename,
            new_filename=new_filename,
            compare_unique_key_result=compare_unique_key_result,
            compare_cols_result=compare_cols_result,
            column_diffs=column_diffs,
            general_observations=general_observations,
        )
