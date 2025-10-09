"""Unit tests for the `df_helpers.py` module."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import polars as pl
import pytest

from table_diff.df_helpers import assert_col_has_no_nulls, assert_unique_key, is_key_unique


def test_always_passes() -> None:
    """Test always passes, as a demo of the test framework."""
    assert True


def test_assert_col_has_no_nulls() -> None:
    """Test that assert_col_has_no_nulls raises an AssertionError when a column has nulls."""
    df = pl.DataFrame({"a": [1, 2, None], "b": [1, 2, 3]})

    with pytest.raises(AssertionError):
        assert_col_has_no_nulls(df, "a")

    # Should not raise an error.
    assert assert_col_has_no_nulls(df, "b") is None


def test_assert_unique_key() -> None:
    """Test that assert_unique_key raises an AssertionError when the unique key has nulls."""
    df = pl.DataFrame({"a": [1, 2, None], "b": [1, 2, 3], "c": [1, 1, 2]})

    with pytest.raises(AssertionError):
        assert_unique_key(df, ["c"])

    # Should not raise an error.
    assert assert_unique_key(df, ["a"]) is None
    assert assert_unique_key(df, ["b"]) is None


def test_is_key_unique() -> None:
    """Test that assert_unique_key raises an AssertionError when the unique key has nulls."""
    df = pl.DataFrame({"a": [1, 2, None], "b": [1, 2, 3], "c": [1, 1, 2]})

    assert is_key_unique(df, ["c"]) is False

    # Should not raise an error.
    assert is_key_unique(df, ["a"]) is True
    assert is_key_unique(df, ["b"]) is True
