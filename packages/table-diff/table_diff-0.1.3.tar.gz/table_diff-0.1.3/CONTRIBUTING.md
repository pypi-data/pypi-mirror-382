# Contributing

Thanks for showing interest in contributing to the `table-diff` project!

## Key Links

* Documentation: Not yet created.
* Bugs and Planning/Communication: Report via [GitLab Issues](https://gitlab.com/parker-research/table-diff/-/issues)

## Testing

Strict testing is not enforced in this project. Tests are implemented with the Pytest unit test framework.

All tests should pass for a contribution to be considered. All features should be well-tested before the contribution is submitted.

Tests are stored in the `tests/` directory.

## Environment Setup

The following steps can be used to configure your development environment.

1. Clone this repository.
2. In this repository, create a virtual environment: `uv venv`
3. Install the Python project in the virtual environment: `uv sync --extra dev --extra pdf`
4. Open this repository in VS Code.
5. Install recommended extension, and use the supplied configuration in the `.vscode/settings.json` file (default behavior).
6. Try running with the sample files provided:

```bash
uv run table_diff ./tests/demo_datasets/populations/city-populations_2010.csv ./tests/demo_datasets/populations/city-populations_2015.csv -u location_id
```

## How to submit changes

Changes should be submitted by forking this repo, branching off of the `main` branch into a feature branch, implementing your change, and submitting a Merge Request back to this upstream project.

Large changes should first be discussed in a relevant GitLab Issue before implementation, as large changes may require planning refactors, or may require planning on an approach which is conducive to the success of the project.

Expect responses in 0-5 days when contributing to this project.

## How to report a bug

Please report bugs by opening a GitLab Issue.

All bug reports will be considered, and will only be closed upon being solved.

Please include steps to reproduce any bugs. Ideally, include sample tables/data as an extension to the Issue.

## How to request an enhancement

Please request enhancements and features by opening a GitLab Issue. Please vote on features by reacting with the 👍 emoji if a feature has been requested but not implemented.

Not all features may be implemented, but all features will be considered.

## Style Guide and Coding Conventions

Ruff, the Python autoformatter and linter, is used in this project. All guidelines must be strictly adhered to.

Pyright, the Python static type checker, is used in this project. All errors must be resolved. This project is strictly typed where possible.

Data-based object oriented code is used. Where possible, data classes are preferred to dictionaries, for example.

All CI/CD pipeline checks should pass before a PR will be merged. The ruff linter/autoformatter, and the Pyright static type checker are used to enforce various quality rules.

## Code of Conduct

Be nice to each other.

## Allowed and Prohibited Content

* Libraries will be accepted on a per-library basis. Library additions should be infrequent.
* Only code which is legally allowed to be used will be accepted.
* AI code generation tools are permitted, but must be acknowledged.
* Copyrighted code not licensed under an appropriate permissive license must not be used in this repository.

## Recognition Model

Thank you for your contributions. Please note that, while I sincerely appreciate any contributions to this project, this project does not have a comprehensive recognition model.
