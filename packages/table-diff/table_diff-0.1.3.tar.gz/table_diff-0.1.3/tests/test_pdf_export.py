"""Helpers for exporting comparison results."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

import tempfile
from pathlib import Path

import pytest

from table_diff.pdf_export import export_markdown_to_pdf


def test_export_to_pdf_creates_file() -> None:
    """Test that export_to_pdf successfully creates a PDF file."""
    line = "Line 1: Comparison result, Line 2: Details, Line 3: Summary"

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_file:
        file_path = Path(temp_file.name)

        export_markdown_to_pdf(line, file_path)

        assert file_path.exists()
        assert file_path.stat().st_size > 100


def test_export_to_pdf_raises_error_with_empty_line() -> None:
    """Test that export_to_pdf raises a ValueError when given an empty line."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_file:
        file_path = Path(temp_file.name)
        with pytest.raises(
            ValueError,
            match=r"Cannot export an empty document to PDF\.",
        ):
            export_markdown_to_pdf("", file_path)
