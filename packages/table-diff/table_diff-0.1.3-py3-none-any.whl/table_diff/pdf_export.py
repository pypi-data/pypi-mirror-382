"""Helpers for exporting comparison results."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Parker L

from pathlib import Path


def export_markdown_to_pdf(markdown_content: str, pdf_file_path: Path) -> None:
    """Write the input markdown document to a PDF.

    Args:
        markdown_content (str): The comparison result to export.
        pdf_file_path (str): The path to save the results to.

    Raises:
        ImportError: If the required module is not installed.
        ValueError: If the line is empty.
        PermissionError: If the file cannot be overwritten.

    """
    try:
        from markdown_pdf import (  # noqa: PLC0415
            MarkdownPdf,
            Section,
        )
    except ImportError as err:
        msg = (
            "Cannot import the required module 'markdown_pdf'. "
            "Consider re-installing table_diff with the optional 'pdf' extra: "
            "`pip install table_diff[pdf]`."
        )
        raise ImportError(msg) from err

    if not markdown_content:
        msg = "Cannot export an empty document to PDF."
        raise ValueError(msg)

    if pdf_file_path.suffix != ".pdf":
        msg = "The file path should end with '.pdf'."
        raise ValueError(msg)

    # Create a MarkdownPdf object and add the content
    pdf = MarkdownPdf()
    section = Section(
        markdown_content,
        paper_size="Letter-L",  # Suffix -L or -P for orientation.
        borders=(16, 16, -16, -16),
    )

    # `border-spacing: -1` is a hack for border-collapse not currently working.
    section_css = """
    table, th, td, tr {
        border: 1px solid black;
        border-collapse: collapse;
        border-spacing: -1;
    }
    td, th {
        overflow: hidden;
        text-overflow: ellipsis;
        word-break: break-word;
        overflow-wrap: anywhere;
        width: 30%;

        text-align: center;
    }
    td, th, p, div, ul, ol, li {
        font-size: 10px;
    }
    """

    pdf.add_section(
        section,
        user_css=section_css,
    )

    # Check if file exists and try to remove it
    if pdf_file_path.exists():
        try:
            pdf_file_path.unlink()
        except PermissionError as err:
            msg = f"Cannot overwrite the file: {pdf_file_path}. It might be open in a viewer."
            raise PermissionError(msg) from err

    # Generate the PDF.
    pdf.save(pdf_file_path)
