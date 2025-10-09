"""Helpers for formatting outputs, especially for logs/as text."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import json
from collections.abc import Iterable
from typing import Any


def format_frac(val: int, total: int, format_str: str = "{val:,} / {total:,} ({frac:.2%})") -> str:
    """Format a fraction as a string.

    Returns:
        The formatted string, like "1,234 / 5,678 (21.73%)".

    """
    return format_str.format(val=val, total=total, frac=val / total)


def format_list_with_count(
    list_val: Iterable[Any],
    unit_singular: str,
    unit_plural: str | None = None,
    *,
    add_parentheses: bool = True,
) -> str:
    """Format a list (or similar), with its count.

    Returns:
        A string like "(3,456 rows): ['a', 'b', 'c']".

    """
    list_val = list(list_val)

    if unit_plural is None:
        unit_plural = unit_singular + "s"

    unit_word = unit_singular if (len(list_val) == 1) else unit_plural

    open_paren = "(" if add_parentheses else ""
    close_paren = ")" if add_parentheses else ""

    return f"{open_paren}{len(list_val):,} {unit_word}{close_paren}: " + json.dumps(list_val)
