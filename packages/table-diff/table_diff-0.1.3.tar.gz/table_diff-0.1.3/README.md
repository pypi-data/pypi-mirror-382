# Table Diff

Table Diff is a Python package that provides a text-based interface for comparing two tables. It is designed to be used by data analysts and data scientists to compare two tables and identify differences between them, especially as transformation rules are adjusted in an ETL pipeline.

The diff between two tables is printed to stdout as Markdown, and can be saved to a Markdown file and/or PDF file.

## Features

* Generate a diff report between two tables.
* View the diff quickly in Markdown.
* Supports the following output formats:
    * Markdown (summary)
    * PDF (summary)
    * DuckDB (comprehensive)
* View common enum/value transitions.

## Getting Started

1. Install Python 3.10 or later, and the `uv` Python package manager.

2. Install this package using `uv tool`:
```bash
uv tool install "table-diff[pdf]"

# Optionally, install without PDF export support:
uv tool install table-diff
```

3. Run the either of the following to compare two tables:
```bash
table_diff <old_csv_path> <new_csv_path> -u PrimaryKeyCol1 PrimaryKeyColN
```

For development environment setup, please refer to the `CONTRIBUTING.md` guide.

## Contributing
Please submit Bug Reports and Merge Requests to the [GitLab project](https://gitlab.com/parker-research/table-diff).

Please refer to the `CONTRIBUTING.md` file for more details about the contribution policy.

## License
This project is licensed using the MIT License. For more information, see the LICENSE file.

Note that this project has been created and modified with the help of Large Language Model (LLM)-based tools like GitHub Copilot and ChatGPT.
